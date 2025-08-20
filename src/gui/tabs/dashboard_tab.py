import customtkinter as ctk

class DashboardTab(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        label = ctk.CTkLabel(self, text="Dashboard Placeholder", font=ctk.CTkFont(size=18, weight="bold"))
        label.pack(pady=20)
    
    def show_info_popup(self):
        """Show information about Dashboard"""
        info_window = ctk.CTkToplevel(self)
        info_window.title("Dashboard - Information")
        info_window.geometry("600x400")
        info_window.transient(self.master)
        info_window.grab_set()
        
        content = ctk.CTkTextbox(info_window, wrap="word")
        content.pack(fill="both", expand=True, padx=20, pady=20)
        
        info_text = """📊 CIOT INVESTIGATION DASHBOARD
═══════════════════════════════════════════════════════════════════════════════

🎯 WHAT IT DOES:
The Dashboard provides a centralized overview of your investigation activities, 
case management, and system status for the Cyber Investigation OSINT Toolkit.

📋 DASHBOARD FEATURES:

🗂️ CASE MANAGEMENT:
   • View active and completed investigation cases
   • Create new investigation cases with detailed metadata
   • Track case progress and status updates
   • Professional case organization and categorization

📊 INVESTIGATION OVERVIEW:
   • Real-time session tracking and statistics
   • Evidence collection summary and metrics
   • Investigation timeline and activity logs
   • Resource utilization and performance monitoring

📈 ANALYTICS & REPORTING:
   • Investigation success rates and completion metrics
   • Evidence integrity verification status
   • Audit trail compliance and logging summary
   • Professional report generation and export options

🔧 SYSTEM STATUS:
   • Application health and performance monitoring
   • Service availability and connectivity status
   • Configuration and settings overview
   • Security and privacy status indicators

🚀 PROFESSIONAL FEATURES:
✓ Centralized case and evidence management
✓ Real-time investigation tracking and monitoring
✓ Professional audit logging and compliance
✓ Comprehensive reporting and analytics
✓ Secure configuration and privacy controls

📋 HOW TO USE THE DASHBOARD:
1. Monitor your active investigations and cases
2. Create new cases using the case management tools
3. Review investigation progress and metrics
4. Generate professional reports for documentation
5. Manage system settings and configuration

⚖️ COMPLIANCE & AUDIT:
The Dashboard maintains comprehensive audit logs and ensures all investigation 
activities comply with professional standards and legal requirements.

This centralized interface helps investigators maintain organization, track progress, 
and ensure professional standards throughout the investigation process."""

        content.insert("1.0", info_text)
        content.configure(state="disabled")
