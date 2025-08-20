"""
Pattern Analysis Engine for Enhanced Phone Investigation

This module provides comprehensive pattern analysis capabilities for phone numbers,
including related number detection, bulk registration analysis, sequential pattern
identification, and carrier block analysis.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict, Counter
import phonenumbers
from phonenumbers import geocoder, carrier


@dataclass
class RelatedNumber:
    """Represents a potentially related phone number with confidence metrics."""
    number: str
    relationship_type: str  # 'sequential', 'bulk_block', 'carrier_block', 'pattern_similar'
    confidence_score: float  # 0.0 to 1.0
    evidence: List[str]  # List of evidence supporting the relationship
    investigation_priority: str  # 'High', 'Medium', 'Low'


@dataclass
class BulkRegistrationBlock:
    """Represents a detected bulk registration block."""
    block_start: str
    block_end: str
    block_size: int
    confidence_score: float
    indicators: List[str]  # Evidence of bulk registration
    risk_assessment: str  # 'Low', 'Medium', 'High', 'Critical'


@dataclass
class SequentialPattern:
    """Represents a sequential number pattern."""
    base_number: str
    sequence_type: str  # 'consecutive', 'increment_pattern', 'alternating'
    pattern_numbers: List[str]
    confidence_score: float
    business_likelihood: float  # Likelihood this is a business registration


@dataclass
class CarrierBlock:
    """Represents a carrier allocation block analysis."""
    carrier_name: str
    block_prefix: str
    allocation_type: str  # 'standard', 'premium', 'bulk', 'special'
    block_characteristics: Dict[str, any]
    confidence_score: float


class PatternAnalysisEngine:
    """
    Advanced pattern analysis engine for phone number investigation.
    
    Provides capabilities for:
    - Related number detection
    - Bulk registration block identification
    - Sequential pattern analysis
    - Carrier block analysis
    - Relationship confidence scoring
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Known carrier prefixes for major countries (can be expanded)
        self.carrier_prefixes = {
            'IN': {
                'Airtel': ['70', '80', '81', '82', '83', '84', '85', '86', '87', '88', '89'],
                'Jio': ['60', '61', '62', '63', '64', '65', '66', '67', '68', '69'],
                'Vodafone': ['90', '91', '92', '93', '94', '95', '96', '97', '98', '99'],
                'BSNL': ['94', '95', '96', '97', '98', '99'],
                'Idea': ['90', '91', '92', '93', '94', '95', '96', '97', '98', '99']
            },
            'US': {
                'Verizon': ['201', '202', '203', '212', '213', '214', '215', '216'],
                'AT&T': ['214', '469', '972', '903', '430', '432', '409', '361'],
                'T-Mobile': ['206', '253', '360', '425', '509', '564', '425']
            }
        }
        
        # Bulk registration indicators
        self.bulk_indicators = [
            'consecutive_sequence',
            'same_carrier_block',
            'registration_time_clustering',
            'similar_usage_patterns',
            'shared_metadata'
        ]
    
    def find_related_numbers(self, phone_number: str, country_code: str = 'IN') -> List[RelatedNumber]:
        """
        Find numbers with similar patterns that might be related accounts.
        
        Args:
            phone_number: The target phone number to analyze
            country_code: ISO country code for context
            
        Returns:
            List of RelatedNumber objects with confidence scores
        """
        try:
            related_numbers = []
            
            # Parse the input number
            parsed_number = self._parse_number(phone_number, country_code)
            if not parsed_number:
                return related_numbers
            
            national_number = str(parsed_number.national_number)
            
            # Find sequential patterns
            sequential_related = self._find_sequential_related(national_number)
            related_numbers.extend(sequential_related)
            
            # Find carrier block related numbers
            carrier_related = self._find_carrier_block_related(parsed_number, country_code)
            related_numbers.extend(carrier_related)
            
            # Find pattern-similar numbers
            pattern_related = self._find_pattern_similar(national_number)
            related_numbers.extend(pattern_related)
            
            # Sort by confidence score (highest first)
            related_numbers.sort(key=lambda x: x.confidence_score, reverse=True)
            
            # Limit to top 20 results to avoid overwhelming the user
            return related_numbers[:20]
            
        except Exception as e:
            self.logger.error(f"Error finding related numbers for {phone_number}: {str(e)}")
            return []
    
    def detect_bulk_registration(self, phone_number: str, country_code: str = 'IN') -> Dict:
        """
        Detect if number belongs to bulk registration blocks.
        
        Args:
            phone_number: The target phone number to analyze
            country_code: ISO country code for context
            
        Returns:
            Dict containing bulk registration analysis results
        """
        try:
            parsed_number = self._parse_number(phone_number, country_code)
            if not parsed_number:
                return {'detected': False, 'reason': 'Invalid phone number'}
            
            national_number = str(parsed_number.national_number)
            
            # Analyze for bulk registration indicators
            bulk_analysis = {
                'detected': False,
                'confidence_score': 0.0,
                'block_info': None,
                'indicators': [],
                'risk_assessment': 'Low',
                'investigation_notes': []
            }
            
            # Check for consecutive number blocks
            consecutive_block = self._detect_consecutive_block(national_number)
            if consecutive_block:
                bulk_analysis['detected'] = True
                bulk_analysis['block_info'] = consecutive_block
                bulk_analysis['indicators'].append('consecutive_sequence')
                bulk_analysis['confidence_score'] += 0.3
            
            # Check for carrier-specific bulk patterns
            carrier_bulk = self._detect_carrier_bulk_pattern(parsed_number, country_code)
            if carrier_bulk:
                bulk_analysis['detected'] = True
                bulk_analysis['indicators'].append('carrier_bulk_pattern')
                bulk_analysis['confidence_score'] += 0.25
                bulk_analysis['investigation_notes'].append(f"Detected in {carrier_bulk['carrier']} bulk allocation")
            
            # Check for number range patterns
            range_pattern = self._detect_range_pattern(national_number)
            if range_pattern:
                bulk_analysis['indicators'].append('range_pattern')
                bulk_analysis['confidence_score'] += 0.2
                bulk_analysis['investigation_notes'].append(f"Part of {range_pattern['pattern_type']} range")
            
            # Assess risk level based on confidence
            if bulk_analysis['confidence_score'] >= 0.7:
                bulk_analysis['risk_assessment'] = 'Critical'
            elif bulk_analysis['confidence_score'] >= 0.5:
                bulk_analysis['risk_assessment'] = 'High'
            elif bulk_analysis['confidence_score'] >= 0.3:
                bulk_analysis['risk_assessment'] = 'Medium'
            
            # Add investigation recommendations
            if bulk_analysis['detected']:
                bulk_analysis['investigation_notes'].append("Recommend checking related numbers in the same block")
                bulk_analysis['investigation_notes'].append("Consider investigating for coordinated activities")
            
            return bulk_analysis
            
        except Exception as e:
            self.logger.error(f"Error detecting bulk registration for {phone_number}: {str(e)}")
            return {'detected': False, 'error': str(e)}
    
    def analyze_sequential_patterns(self, phone_number: str, country_code: str = 'IN') -> Dict:
        """
        Analyze sequential number patterns for consecutive number ranges.
        
        Args:
            phone_number: The target phone number to analyze
            country_code: ISO country code for context
            
        Returns:
            Dict containing sequential pattern analysis results
        """
        try:
            parsed_number = self._parse_number(phone_number, country_code)
            if not parsed_number:
                return {'found': False, 'reason': 'Invalid phone number'}
            
            national_number = str(parsed_number.national_number)
            
            sequential_analysis = {
                'found': False,
                'patterns': [],
                'confidence_score': 0.0,
                'business_likelihood': 0.0,
                'investigation_priority': 'Low'
            }
            
            # Detect consecutive sequences
            consecutive_patterns = self._find_consecutive_sequences(national_number)
            if consecutive_patterns:
                sequential_analysis['found'] = True
                sequential_analysis['patterns'].extend(consecutive_patterns)
                sequential_analysis['confidence_score'] += 0.4
            
            # Detect increment patterns (e.g., +10, +100 patterns)
            increment_patterns = self._find_increment_patterns(national_number)
            if increment_patterns:
                sequential_analysis['found'] = True
                sequential_analysis['patterns'].extend(increment_patterns)
                sequential_analysis['confidence_score'] += 0.3
            
            # Detect alternating patterns
            alternating_patterns = self._find_alternating_patterns(national_number)
            if alternating_patterns:
                sequential_analysis['found'] = True
                sequential_analysis['patterns'].extend(alternating_patterns)
                sequential_analysis['confidence_score'] += 0.2
            
            # Assess business likelihood
            if sequential_analysis['found']:
                business_indicators = self._assess_business_likelihood(national_number, sequential_analysis['patterns'])
                sequential_analysis['business_likelihood'] = business_indicators['likelihood']
                
                # Set investigation priority
                if sequential_analysis['confidence_score'] >= 0.6 and business_indicators['likelihood'] >= 0.7:
                    sequential_analysis['investigation_priority'] = 'High'
                elif sequential_analysis['confidence_score'] >= 0.4:
                    sequential_analysis['investigation_priority'] = 'Medium'
            
            return sequential_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing sequential patterns for {phone_number}: {str(e)}")
            return {'found': False, 'error': str(e)}
    
    def analyze_carrier_block(self, phone_number: str, country_code: str = 'IN') -> Dict:
        """
        Detect if number is part of a specific carrier allocation block.
        
        Args:
            phone_number: The target phone number to analyze
            country_code: ISO country code for context
            
        Returns:
            Dict containing carrier block analysis results
        """
        try:
            parsed_number = self._parse_number(phone_number, country_code)
            if not parsed_number:
                return {'detected': False, 'reason': 'Invalid phone number'}
            
            national_number = str(parsed_number.national_number)
            
            # Get carrier information
            carrier_name = carrier.name_for_number(parsed_number, 'en')
            
            carrier_analysis = {
                'detected': False,
                'carrier_name': carrier_name or 'Unknown',
                'block_info': {},
                'allocation_type': 'standard',
                'confidence_score': 0.0,
                'characteristics': {}
            }
            
            # Analyze carrier-specific patterns
            if country_code in self.carrier_prefixes:
                carrier_patterns = self._analyze_carrier_patterns(national_number, country_code)
                if carrier_patterns:
                    carrier_analysis['detected'] = True
                    carrier_analysis['block_info'] = carrier_patterns
                    carrier_analysis['confidence_score'] = carrier_patterns.get('confidence', 0.0)
            
            # Detect special allocation types
            allocation_type = self._detect_allocation_type(national_number, country_code)
            carrier_analysis['allocation_type'] = allocation_type['type']
            carrier_analysis['characteristics'] = allocation_type['characteristics']
            
            if allocation_type['type'] != 'standard':
                carrier_analysis['detected'] = True
                carrier_analysis['confidence_score'] += 0.3
            
            return carrier_analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing carrier block for {phone_number}: {str(e)}")
            return {'detected': False, 'error': str(e)}
    
    def calculate_relationship_confidence(self, number1: str, number2: str, country_code: str = 'IN') -> float:
        """
        Calculate confidence score for relationship between two numbers.
        
        Args:
            number1: First phone number
            number2: Second phone number
            country_code: ISO country code for context
            
        Returns:
            Float confidence score between 0.0 and 1.0
        """
        try:
            parsed1 = self._parse_number(number1, country_code)
            parsed2 = self._parse_number(number2, country_code)
            
            if not parsed1 or not parsed2:
                return 0.0
            
            national1 = str(parsed1.national_number)
            national2 = str(parsed2.national_number)
            
            confidence = 0.0
            
            # Check for sequential relationship
            if self._are_sequential(national1, national2):
                confidence += 0.4
            
            # Check for same carrier
            carrier1 = carrier.name_for_number(parsed1, 'en')
            carrier2 = carrier.name_for_number(parsed2, 'en')
            if carrier1 and carrier2 and carrier1 == carrier2:
                confidence += 0.2
            
            # Check for same geographic region
            region1 = geocoder.description_for_number(parsed1, 'en')
            region2 = geocoder.description_for_number(parsed2, 'en')
            if region1 and region2 and region1 == region2:
                confidence += 0.15
            
            # Check for pattern similarity
            pattern_similarity = self._calculate_pattern_similarity(national1, national2)
            confidence += pattern_similarity * 0.25
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating relationship confidence: {str(e)}")
            return 0.0
    
    def suggest_investigation_priorities(self, analysis_results: Dict) -> List[Dict]:
        """
        Suggest investigation priorities based on pattern analysis results.
        
        Args:
            analysis_results: Combined results from pattern analysis
            
        Returns:
            List of investigation priority suggestions
        """
        priorities = []
        
        try:
            # High priority: Bulk registration with high confidence
            if (analysis_results.get('bulk_registration', {}).get('detected') and 
                analysis_results.get('bulk_registration', {}).get('confidence_score', 0) >= 0.7):
                priorities.append({
                    'priority': 'High',
                    'type': 'Bulk Registration Investigation',
                    'description': 'Number appears to be part of a bulk registration block with high confidence',
                    'recommended_actions': [
                        'Investigate other numbers in the same block',
                        'Check for coordinated activities',
                        'Analyze registration timing patterns'
                    ]
                })
            
            # Medium priority: Sequential patterns with business likelihood
            if (analysis_results.get('sequential_patterns', {}).get('found') and 
                analysis_results.get('sequential_patterns', {}).get('business_likelihood', 0) >= 0.6):
                priorities.append({
                    'priority': 'Medium',
                    'type': 'Business Connection Investigation',
                    'description': 'Sequential patterns suggest possible business or organizational connection',
                    'recommended_actions': [
                        'Investigate related sequential numbers',
                        'Check for business registration records',
                        'Analyze usage patterns for business indicators'
                    ]
                })
            
            # Medium priority: Related numbers with high confidence
            related_numbers = analysis_results.get('related_numbers', [])
            high_confidence_related = [r for r in related_numbers if r.confidence_score >= 0.7]
            if high_confidence_related:
                priorities.append({
                    'priority': 'Medium',
                    'type': 'Related Number Investigation',
                    'description': f'Found {len(high_confidence_related)} highly related numbers',
                    'recommended_actions': [
                        'Investigate each related number individually',
                        'Look for common usage patterns',
                        'Check for shared metadata or registration info'
                    ]
                })
            
            # Low priority: Carrier block analysis
            if analysis_results.get('carrier_block', {}).get('detected'):
                priorities.append({
                    'priority': 'Low',
                    'type': 'Carrier Block Analysis',
                    'description': 'Number belongs to specific carrier allocation block',
                    'recommended_actions': [
                        'Research carrier allocation policies',
                        'Check for other numbers in same block',
                        'Analyze block characteristics'
                    ]
                })
            
            # Sort by priority (High -> Medium -> Low)
            priority_order = {'High': 3, 'Medium': 2, 'Low': 1}
            priorities.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
            
            return priorities
            
        except Exception as e:
            self.logger.error(f"Error suggesting investigation priorities: {str(e)}")
            return []
    
    # Private helper methods
    
    def _parse_number(self, phone_number: str, country_code: str) -> Optional[phonenumbers.PhoneNumber]:
        """Parse phone number using phonenumbers library."""
        try:
            return phonenumbers.parse(phone_number, country_code)
        except:
            return None
    
    def _find_sequential_related(self, national_number: str) -> List[RelatedNumber]:
        """Find sequentially related numbers."""
        related = []
        base_num = int(national_number)
        
        # Check numbers within +/- 10 range
        for offset in range(-10, 11):
            if offset == 0:
                continue
            
            candidate = str(base_num + offset)
            if len(candidate) == len(national_number):
                confidence = max(0.1, 1.0 - abs(offset) * 0.1)
                related.append(RelatedNumber(
                    number=candidate,
                    relationship_type='sequential',
                    confidence_score=confidence,
                    evidence=[f"Sequential offset: {offset}"],
                    investigation_priority='Medium' if abs(offset) <= 5 else 'Low'
                ))
        
        return related
    
    def _find_carrier_block_related(self, parsed_number: phonenumbers.PhoneNumber, country_code: str) -> List[RelatedNumber]:
        """Find numbers in the same carrier block."""
        related = []
        
        try:
            carrier_name = carrier.name_for_number(parsed_number, 'en')
            if not carrier_name:
                return related
            
            national_number = str(parsed_number.national_number)
            
            # For demonstration, generate some carrier block related numbers
            # In a real implementation, this would query actual carrier databases
            prefix = national_number[:6]  # First 6 digits as block identifier
            
            for i in range(1, 6):  # Generate 5 potential related numbers
                candidate = prefix + str(int(national_number[6:]) + i * 100).zfill(len(national_number) - 6)
                if len(candidate) == len(national_number):
                    related.append(RelatedNumber(
                        number=candidate,
                        relationship_type='carrier_block',
                        confidence_score=0.6,
                        evidence=[f"Same carrier block: {carrier_name}", f"Shared prefix: {prefix}"],
                        investigation_priority='Medium'
                    ))
        
        except Exception as e:
            self.logger.error(f"Error finding carrier block related numbers: {str(e)}")
        
        return related
    
    def _find_pattern_similar(self, national_number: str) -> List[RelatedNumber]:
        """Find numbers with similar digit patterns."""
        related = []
        
        # Analyze digit patterns
        digit_pattern = self._extract_digit_pattern(national_number)
        
        # Generate similar pattern numbers (simplified for demonstration)
        for variation in self._generate_pattern_variations(national_number, digit_pattern):
            if variation != national_number:
                similarity = self._calculate_pattern_similarity(national_number, variation)
                if similarity >= 0.5:
                    related.append(RelatedNumber(
                        number=variation,
                        relationship_type='pattern_similar',
                        confidence_score=similarity,
                        evidence=[f"Pattern similarity: {similarity:.2f}"],
                        investigation_priority='Low'
                    ))
        
        return related[:5]  # Limit to top 5 pattern matches
    
    def _detect_consecutive_block(self, national_number: str) -> Optional[BulkRegistrationBlock]:
        """Detect if number is part of a consecutive block."""
        base_num = int(national_number)
        
        # Simple heuristic: check if number ends in patterns suggesting bulk registration
        last_digits = base_num % 1000
        
        if last_digits < 100 and last_digits % 10 == 0:  # Ends in X0, X00, etc.
            return BulkRegistrationBlock(
                block_start=str(base_num - last_digits),
                block_end=str(base_num - last_digits + 999),
                block_size=1000,
                confidence_score=0.7,
                indicators=['consecutive_pattern', 'round_number_ending'],
                risk_assessment='Medium'
            )
        
        return None
    
    def _detect_carrier_bulk_pattern(self, parsed_number: phonenumbers.PhoneNumber, country_code: str) -> Optional[Dict]:
        """Detect carrier-specific bulk patterns."""
        national_number = str(parsed_number.national_number)
        carrier_name = carrier.name_for_number(parsed_number, 'en')
        
        if not carrier_name:
            return None
        
        # Check if number fits known bulk allocation patterns
        if country_code == 'IN' and len(national_number) == 10:
            prefix = national_number[:4]
            
            # Known bulk prefixes (simplified)
            bulk_prefixes = ['9000', '9001', '9002', '8000', '8001', '7000']
            
            if prefix in bulk_prefixes:
                return {
                    'carrier': carrier_name,
                    'bulk_prefix': prefix,
                    'confidence': 0.8
                }
        
        return None
    
    def _detect_range_pattern(self, national_number: str) -> Optional[Dict]:
        """Detect if number is part of a specific range pattern."""
        # Check for patterns like all same digits, ascending/descending sequences
        digits = list(national_number)
        
        # All same digits
        if len(set(digits)) == 1:
            return {'pattern_type': 'all_same_digits', 'confidence': 0.9}
        
        # Ascending sequence
        if all(int(digits[i]) <= int(digits[i+1]) for i in range(len(digits)-1)):
            return {'pattern_type': 'ascending_sequence', 'confidence': 0.8}
        
        # Descending sequence
        if all(int(digits[i]) >= int(digits[i+1]) for i in range(len(digits)-1)):
            return {'pattern_type': 'descending_sequence', 'confidence': 0.8}
        
        return None
    
    def _find_consecutive_sequences(self, national_number: str) -> List[SequentialPattern]:
        """Find consecutive number sequences."""
        patterns = []
        base_num = int(national_number)
        
        # Generate consecutive sequences
        for start_offset in [-5, -10, -20]:
            sequence_numbers = []
            for i in range(10):  # 10 consecutive numbers
                seq_num = str(base_num + start_offset + i)
                if len(seq_num) == len(national_number):
                    sequence_numbers.append(seq_num)
            
            if national_number in sequence_numbers:
                patterns.append(SequentialPattern(
                    base_number=national_number,
                    sequence_type='consecutive',
                    pattern_numbers=sequence_numbers,
                    confidence_score=0.8,
                    business_likelihood=0.6
                ))
        
        return patterns
    
    def _find_increment_patterns(self, national_number: str) -> List[SequentialPattern]:
        """Find increment patterns (e.g., +10, +100)."""
        patterns = []
        base_num = int(national_number)
        
        for increment in [10, 100, 1000]:
            pattern_numbers = []
            for i in range(-2, 3):  # 5 numbers in pattern
                pattern_num = str(base_num + i * increment)
                if len(pattern_num) == len(national_number):
                    pattern_numbers.append(pattern_num)
            
            if national_number in pattern_numbers:
                patterns.append(SequentialPattern(
                    base_number=national_number,
                    sequence_type='increment_pattern',
                    pattern_numbers=pattern_numbers,
                    confidence_score=0.6,
                    business_likelihood=0.7
                ))
        
        return patterns
    
    def _find_alternating_patterns(self, national_number: str) -> List[SequentialPattern]:
        """Find alternating digit patterns."""
        patterns = []
        
        # Check for alternating patterns in the number
        digits = list(national_number)
        alternating_detected = False
        
        # Simple alternating pattern detection
        if len(digits) >= 4:
            for i in range(len(digits) - 3):
                if digits[i] == digits[i+2] and digits[i+1] == digits[i+3] and digits[i] != digits[i+1]:
                    alternating_detected = True
                    break
        
        if alternating_detected:
            patterns.append(SequentialPattern(
                base_number=national_number,
                sequence_type='alternating',
                pattern_numbers=[national_number],  # Would generate variations in real implementation
                confidence_score=0.5,
                business_likelihood=0.3
            ))
        
        return patterns
    
    def _assess_business_likelihood(self, national_number: str, patterns: List[SequentialPattern]) -> Dict:
        """Assess likelihood that patterns indicate business registration."""
        likelihood = 0.0
        indicators = []
        
        # Business indicators
        if any(p.sequence_type == 'consecutive' for p in patterns):
            likelihood += 0.3
            indicators.append('consecutive_sequence')
        
        if any(p.sequence_type == 'increment_pattern' for p in patterns):
            likelihood += 0.4
            indicators.append('increment_pattern')
        
        # Round number endings suggest business
        if national_number.endswith(('00', '000')):
            likelihood += 0.2
            indicators.append('round_ending')
        
        # Repeating digits suggest intentional selection
        digit_counts = Counter(national_number)
        if any(count >= 4 for count in digit_counts.values()):
            likelihood += 0.1
            indicators.append('repeating_digits')
        
        return {
            'likelihood': min(likelihood, 1.0),
            'indicators': indicators
        }
    
    def _analyze_carrier_patterns(self, national_number: str, country_code: str) -> Optional[Dict]:
        """Analyze carrier-specific allocation patterns."""
        if country_code not in self.carrier_prefixes:
            return None
        
        # Check against known carrier prefixes
        for carrier_name, prefixes in self.carrier_prefixes[country_code].items():
            for prefix in prefixes:
                if national_number.startswith(prefix):
                    return {
                        'carrier': carrier_name,
                        'prefix': prefix,
                        'confidence': 0.8,
                        'allocation_info': f"Standard {carrier_name} allocation"
                    }
        
        return None
    
    def _detect_allocation_type(self, national_number: str, country_code: str) -> Dict:
        """Detect the type of number allocation."""
        allocation_info = {
            'type': 'standard',
            'characteristics': {}
        }
        
        # Premium numbers (simplified detection)
        if country_code == 'IN' and national_number.startswith(('1800', '1860')):
            allocation_info['type'] = 'toll_free'
            allocation_info['characteristics']['cost'] = 'free'
        elif national_number.startswith('900'):
            allocation_info['type'] = 'premium'
            allocation_info['characteristics']['cost'] = 'premium_rate'
        
        # VoIP detection (simplified)
        voip_prefixes = ['560', '561', '562']  # Example VoIP prefixes
        if any(national_number.startswith(prefix) for prefix in voip_prefixes):
            allocation_info['type'] = 'voip'
            allocation_info['characteristics']['technology'] = 'voice_over_ip'
        
        return allocation_info
    
    def _are_sequential(self, number1: str, number2: str) -> bool:
        """Check if two numbers are sequential."""
        try:
            num1, num2 = int(number1), int(number2)
            return abs(num1 - num2) <= 10
        except:
            return False
    
    def _extract_digit_pattern(self, number: str) -> str:
        """Extract digit pattern from number."""
        # Simplified pattern extraction
        pattern = ""
        for i, digit in enumerate(number):
            if i == 0:
                pattern += digit
            elif digit == number[i-1]:
                pattern += "R"  # Repeat
            elif int(digit) == int(number[i-1]) + 1:
                pattern += "+"  # Increment
            elif int(digit) == int(number[i-1]) - 1:
                pattern += "-"  # Decrement
            else:
                pattern += "X"  # Different
        return pattern
    
    def _generate_pattern_variations(self, number: str, pattern: str) -> List[str]:
        """Generate variations based on digit pattern."""
        # Simplified variation generation
        variations = []
        base_num = int(number)
        
        # Generate some variations by modifying last few digits
        for offset in [-5, -3, -1, 1, 3, 5]:
            variation = str(base_num + offset)
            if len(variation) == len(number):
                variations.append(variation)
        
        return variations
    
    def _calculate_pattern_similarity(self, number1: str, number2: str) -> float:
        """Calculate similarity between two number patterns."""
        if len(number1) != len(number2):
            return 0.0
        
        matches = sum(1 for a, b in zip(number1, number2) if a == b)
        return matches / len(number1)