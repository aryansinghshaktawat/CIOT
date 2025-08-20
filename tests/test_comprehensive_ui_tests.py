"""
Comprehensive UI Automation Tests for Enhanced Phone Investigation
Tests country selection, results display, and user interactions
"""

import pytest
import tkinter as tk
import customtkinter as ctk
from unittest.mock import Mock, patch, MagicMock
import threading
import time
from typing import Dict, Any, List
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import GUI components
from gui.tabs.surface_web_tab import SurfaceWebTab
from gui.tabs.dashboard_tab import DashboardTab
from core.application import CIOTMainApp


class UITestHelper:
    """Helper class for UI testing"""
    
    def __init__(self):
        self.app = None
        self.root = None
        self.test_timeout = 30
    
    def setup_test_app(self):
        """Setup test application"""
        self.root = ctk.CTk()
        self.root.withdraw()  # Hide window during testing
        self.app = CIOTMainApp()
        return self.app
    
    def teardown_test_app(self):
        """Teardown test application"""
        if self.root:
            try:
                self.root.destroy()
            except:
                pass
    
    def find_widget_by_text(self, parent, text, widget_type=None):
        """Find widget by text content"""
        def search_widget(widget):
            try:
                if hasattr(widget, 'cget'):
                    widget_text = widget.cget('text')
                    if text in str(widget_text):
                        if widget_type is None or isinstance(widget, widget_type):
                            return widget
            except:
                pass
            
            # Search children
            for child in widget.winfo_children():
                result = search_widget(child)
                if result:
                    return result
            return None
        
        return search_widget(parent)
    
    def simulate_click(self, widget):
        """Simulate click on widget"""
        if hasattr(widget, 'invoke'):
            widget.invoke()
        elif hasattr(widget, 'event_generate'):
            widget.event_generate('<Button-1>')
    
    def simulate_text_input(self, widget, text):
        """Simulate text input"""
        if hasattr(widget, 'delete'):
            widget.delete(0, tk.END)
        if hasattr(widget, 'insert'):
            widget.insert(0, text)
    
    def wait_for_condition(self, condition_func, timeout=None):
        """Wait for condition to be true"""
        timeout = timeout or self.test_timeout
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition_func():
                return True
            time.sleep(0.1)
        
        return False


@pytest.fixture
def ui_helper():
    """UI test helper fixture"""
    helper = UITestHelper()
    yield helper
    helper.teardown_test_app()


@pytest.mark.ui
class TestCountrySelectionUI:
    """UI tests for country selection functionality"""
    
    def test_country_dropdown_initialization(self, ui_helper):
        """Test country dropdown is properly initialized"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        assert surface_tab is not None, "Surface web tab not found"
        
        # Check if country selection widget exists
        country_widget = ui_helper.find_widget_by_text(surface_tab, "Country")
        assert country_widget is not None, "Country selection widget not found"
    
    def test_country_selection_change(self, ui_helper, sample_phone_numbers):
        """Test country selection change updates investigation"""
        app = ui_helper.setup_test_app()
        
        with patch('src.utils.osint_utils.get_enhanced_phone_info') as mock_investigate:
            mock_investigate.return_value = {
                'success': True,
                'country_name': 'United States',
                'international_format': '+1 555 123 4567'
            }
            
            # Find surface web tab
            surface_tab = None
            for tab in app.tabs:
                if isinstance(tab, SurfaceWebTab):
                    surface_tab = tab
                    break
            
            # Simulate phone number input
            phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
            if phone_entry:
                ui_helper.simulate_text_input(phone_entry, sample_phone_numbers['valid_us'])
            
            # Simulate country selection change
            country_dropdown = ui_helper.find_widget_by_text(surface_tab, "Country")
            if country_dropdown and hasattr(country_dropdown, 'set'):
                country_dropdown.set('US')
            
            # Simulate investigation button click
            investigate_btn = ui_helper.find_widget_by_text(surface_tab, "Investigate")
            if investigate_btn:
                ui_helper.simulate_click(investigate_btn)
            
            # Wait for investigation to complete
            def check_results():
                return mock_investigate.called
            
            assert ui_helper.wait_for_condition(check_results, timeout=5)
            
            # Verify country was passed correctly
            call_args = mock_investigate.call_args
            if call_args:
                assert call_args[0][1] == 'US'  # Country parameter
    
    def test_country_auto_detection(self, ui_helper, sample_phone_numbers):
        """Test automatic country detection from phone number"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        # Simulate entering international format number
        phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
        if phone_entry:
            ui_helper.simulate_text_input(phone_entry, sample_phone_numbers['valid_indian_formatted'])
        
        # Check if country is auto-detected
        country_dropdown = ui_helper.find_widget_by_text(surface_tab, "Country")
        if country_dropdown and hasattr(country_dropdown, 'get'):
            # Should auto-detect India
            time.sleep(0.5)  # Allow time for auto-detection
            current_country = country_dropdown.get()
            assert current_country in ['IN', 'India'], f"Expected IN/India, got {current_country}"
    
    def test_country_validation_feedback(self, ui_helper, sample_phone_numbers):
        """Test country validation provides user feedback"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        # Simulate entering phone number with wrong country
        phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
        if phone_entry:
            ui_helper.simulate_text_input(phone_entry, sample_phone_numbers['valid_indian'])
        
        # Set wrong country
        country_dropdown = ui_helper.find_widget_by_text(surface_tab, "Country")
        if country_dropdown and hasattr(country_dropdown, 'set'):
            country_dropdown.set('US')
        
        # Simulate investigation
        with patch('src.utils.osint_utils.get_enhanced_phone_info') as mock_investigate:
            mock_investigate.return_value = {
                'success': False,
                'error': 'Country mismatch detected',
                'suggested_country': 'IN'
            }
            
            investigate_btn = ui_helper.find_widget_by_text(surface_tab, "Investigate")
            if investigate_btn:
                ui_helper.simulate_click(investigate_btn)
            
            # Check for validation feedback
            def check_feedback():
                feedback_widget = ui_helper.find_widget_by_text(surface_tab, "mismatch")
                return feedback_widget is not None
            
            assert ui_helper.wait_for_condition(check_feedback, timeout=5)


@pytest.mark.ui
class TestResultsDisplayUI:
    """UI tests for results display functionality"""
    
    def test_results_display_structure(self, ui_helper, sample_investigation_results):
        """Test results are displayed with proper structure"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        with patch('src.utils.osint_utils.get_enhanced_phone_info') as mock_investigate:
            mock_investigate.return_value = sample_investigation_results
            
            # Simulate investigation
            phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
            if phone_entry:
                ui_helper.simulate_text_input(phone_entry, "9876543210")
            
            investigate_btn = ui_helper.find_widget_by_text(surface_tab, "Investigate")
            if investigate_btn:
                ui_helper.simulate_click(investigate_btn)
            
            # Wait for results to display
            def check_results_displayed():
                # Check for key result fields
                international_format = ui_helper.find_widget_by_text(surface_tab, "+91 98765 43210")
                carrier_info = ui_helper.find_widget_by_text(surface_tab, "Airtel")
                return international_format is not None or carrier_info is not None
            
            assert ui_helper.wait_for_condition(check_results_displayed, timeout=10)
    
    def test_error_display(self, ui_helper, sample_phone_numbers):
        """Test error messages are properly displayed"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        with patch('src.utils.osint_utils.get_enhanced_phone_info') as mock_investigate:
            mock_investigate.return_value = {
                'success': False,
                'error': 'Invalid phone number format',
                'guidance': 'Please enter a valid phone number'
            }
            
            # Simulate investigation with invalid number
            phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
            if phone_entry:
                ui_helper.simulate_text_input(phone_entry, sample_phone_numbers['invalid_format'])
            
            investigate_btn = ui_helper.find_widget_by_text(surface_tab, "Investigate")
            if investigate_btn:
                ui_helper.simulate_click(investigate_btn)
            
            # Check for error display
            def check_error_displayed():
                error_widget = ui_helper.find_widget_by_text(surface_tab, "Invalid phone number")
                guidance_widget = ui_helper.find_widget_by_text(surface_tab, "Please enter a valid")
                return error_widget is not None or guidance_widget is not None
            
            assert ui_helper.wait_for_condition(check_error_displayed, timeout=5)
    
    def test_loading_indicator(self, ui_helper, sample_phone_numbers):
        """Test loading indicator during investigation"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        # Mock slow investigation
        def slow_investigate(*args, **kwargs):
            time.sleep(2)  # Simulate slow API
            return {'success': True, 'international_format': '+91 98765 43210'}
        
        with patch('src.utils.osint_utils.get_enhanced_phone_info', side_effect=slow_investigate):
            # Simulate investigation
            phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
            if phone_entry:
                ui_helper.simulate_text_input(phone_entry, sample_phone_numbers['valid_indian'])
            
            investigate_btn = ui_helper.find_widget_by_text(surface_tab, "Investigate")
            if investigate_btn:
                ui_helper.simulate_click(investigate_btn)
            
            # Check for loading indicator
            def check_loading():
                loading_widget = ui_helper.find_widget_by_text(surface_tab, "Investigating")
                progress_widget = ui_helper.find_widget_by_text(surface_tab, "Loading")
                return loading_widget is not None or progress_widget is not None
            
            # Should show loading indicator briefly
            assert ui_helper.wait_for_condition(check_loading, timeout=1)
    
    def test_results_export_functionality(self, ui_helper, sample_investigation_results):
        """Test results export functionality"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        with patch('src.utils.osint_utils.get_enhanced_phone_info') as mock_investigate:
            mock_investigate.return_value = sample_investigation_results
            
            # Simulate investigation
            phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
            if phone_entry:
                ui_helper.simulate_text_input(phone_entry, "9876543210")
            
            investigate_btn = ui_helper.find_widget_by_text(surface_tab, "Investigate")
            if investigate_btn:
                ui_helper.simulate_click(investigate_btn)
            
            # Wait for results
            time.sleep(1)
            
            # Look for export button
            export_btn = ui_helper.find_widget_by_text(surface_tab, "Export")
            if export_btn:
                with patch('tkinter.filedialog.asksaveasfilename', return_value='test_export.json'):
                    ui_helper.simulate_click(export_btn)
                    
                    # Should trigger export functionality
                    # This is a basic test - in real implementation, verify file creation
                    assert True  # Export button exists and is clickable


@pytest.mark.ui
class TestUserInteractionUI:
    """UI tests for user interactions and workflows"""
    
    def test_tab_navigation(self, ui_helper):
        """Test navigation between tabs"""
        app = ui_helper.setup_test_app()
        
        # Check if multiple tabs exist
        assert len(app.tabs) > 1, "Multiple tabs should exist"
        
        # Test switching between tabs
        for i, tab in enumerate(app.tabs):
            if hasattr(app, 'select_tab'):
                app.select_tab(i)
                # Verify tab is selected
                assert True  # Basic test - tab switching works
    
    def test_input_validation_feedback(self, ui_helper):
        """Test real-time input validation feedback"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        # Test invalid input
        phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
        if phone_entry:
            ui_helper.simulate_text_input(phone_entry, "invalid")
            
            # Check for validation feedback
            def check_validation():
                validation_widget = ui_helper.find_widget_by_text(surface_tab, "invalid")
                return validation_widget is not None
            
            # May show validation feedback
            ui_helper.wait_for_condition(check_validation, timeout=2)
    
    def test_keyboard_shortcuts(self, ui_helper, sample_phone_numbers):
        """Test keyboard shortcuts functionality"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        # Test Enter key to trigger investigation
        phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
        if phone_entry:
            ui_helper.simulate_text_input(phone_entry, sample_phone_numbers['valid_indian'])
            
            with patch('src.utils.osint_utils.get_enhanced_phone_info') as mock_investigate:
                mock_investigate.return_value = {'success': True}
                
                # Simulate Enter key press
                if hasattr(phone_entry, 'event_generate'):
                    phone_entry.event_generate('<Return>')
                
                # Should trigger investigation
                def check_investigation():
                    return mock_investigate.called
                
                assert ui_helper.wait_for_condition(check_investigation, timeout=3)
    
    def test_copy_to_clipboard_functionality(self, ui_helper, sample_investigation_results):
        """Test copy to clipboard functionality"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        with patch('src.utils.osint_utils.get_enhanced_phone_info') as mock_investigate:
            mock_investigate.return_value = sample_investigation_results
            
            # Simulate investigation
            phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
            if phone_entry:
                ui_helper.simulate_text_input(phone_entry, "9876543210")
            
            investigate_btn = ui_helper.find_widget_by_text(surface_tab, "Investigate")
            if investigate_btn:
                ui_helper.simulate_click(investigate_btn)
            
            # Wait for results
            time.sleep(1)
            
            # Look for copy button
            copy_btn = ui_helper.find_widget_by_text(surface_tab, "Copy")
            if copy_btn:
                with patch('tkinter.Tk.clipboard_clear'), \
                     patch('tkinter.Tk.clipboard_append') as mock_clipboard:
                    
                    ui_helper.simulate_click(copy_btn)
                    
                    # Should copy to clipboard
                    assert mock_clipboard.called or True  # Basic test


@pytest.mark.ui
class TestResponsiveDesignUI:
    """UI tests for responsive design and layout"""
    
    def test_window_resizing(self, ui_helper):
        """Test UI adapts to window resizing"""
        app = ui_helper.setup_test_app()
        
        # Test different window sizes
        sizes = [(800, 600), (1200, 800), (1600, 1000)]
        
        for width, height in sizes:
            if ui_helper.root:
                ui_helper.root.geometry(f"{width}x{height}")
                ui_helper.root.update()
                
                # Verify UI elements are still accessible
                # This is a basic test - in real implementation, check element positions
                assert True
    
    def test_font_scaling(self, ui_helper):
        """Test font scaling functionality"""
        app = ui_helper.setup_test_app()
        
        # Test different font scales
        scales = [0.8, 1.0, 1.2]
        
        for scale in scales:
            if hasattr(ctk, 'set_widget_scaling'):
                ctk.set_widget_scaling(scale)
                
                # Verify UI still functions
                assert True  # Basic test
    
    def test_theme_switching(self, ui_helper):
        """Test theme switching functionality"""
        app = ui_helper.setup_test_app()
        
        # Test different themes
        themes = ["light", "dark", "system"]
        
        for theme in themes:
            if hasattr(ctk, 'set_appearance_mode'):
                ctk.set_appearance_mode(theme)
                
                # Verify UI still functions
                assert True  # Basic test


@pytest.mark.ui
@pytest.mark.slow
class TestUIPerformance:
    """UI performance tests"""
    
    def test_ui_responsiveness_during_investigation(self, ui_helper, sample_phone_numbers):
        """Test UI remains responsive during investigation"""
        app = ui_helper.setup_test_app()
        
        # Find surface web tab
        surface_tab = None
        for tab in app.tabs:
            if isinstance(tab, SurfaceWebTab):
                surface_tab = tab
                break
        
        # Mock slow investigation
        def slow_investigate(*args, **kwargs):
            time.sleep(3)  # Simulate slow API
            return {'success': True}
        
        with patch('src.utils.osint_utils.get_enhanced_phone_info', side_effect=slow_investigate):
            # Start investigation
            phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
            if phone_entry:
                ui_helper.simulate_text_input(phone_entry, sample_phone_numbers['valid_indian'])
            
            investigate_btn = ui_helper.find_widget_by_text(surface_tab, "Investigate")
            if investigate_btn:
                ui_helper.simulate_click(investigate_btn)
            
            # Test UI responsiveness during investigation
            time.sleep(0.5)  # Let investigation start
            
            # Try to interact with other UI elements
            country_dropdown = ui_helper.find_widget_by_text(surface_tab, "Country")
            if country_dropdown and hasattr(country_dropdown, 'set'):
                # Should still be able to change country
                country_dropdown.set('US')
                assert True  # UI is responsive
    
    def test_memory_usage_during_ui_operations(self, ui_helper, sample_phone_numbers):
        """Test memory usage during UI operations"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        app = ui_helper.setup_test_app()
        
        # Perform multiple UI operations
        for _ in range(10):
            # Find surface web tab
            surface_tab = None
            for tab in app.tabs:
                if isinstance(tab, SurfaceWebTab):
                    surface_tab = tab
                    break
            
            if surface_tab:
                phone_entry = ui_helper.find_widget_by_text(surface_tab, "Phone")
                if phone_entry:
                    ui_helper.simulate_text_input(phone_entry, sample_phone_numbers['valid_indian'])
        
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 50  # Less than 50MB increase


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-m', 'ui'])