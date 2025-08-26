"""
Size recommender for virtual try-on processing

Provides intelligent size recommendations based on:
- Fit analysis results
- User measurements
- Garment properties
- Historical fit data
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional
import asyncio

from ..core.models import (
    ProcessingRequest, FitAnalysis, SizeRecommendation,
    UserMeasurements, GarmentType, FabricMaterial
)
from ..utils.config import get_settings

logger = logging.getLogger(__name__)

class SizeRecommender:
    """
    Provides size recommendations for garments
    
    Analyzes fit data and user measurements to suggest:
    - Optimal size for current garment
    - Alternative sizes to try
    - Size adjustment recommendations
    """
    
    def __init__(self):
        self.settings = get_settings()
        self.models_loaded = False
        
        # Size recommendation parameters
        self.size_model = self.settings.SIZE_RECOMMENDATION_MODEL
        
        # AI models (placeholder for actual model loading)
        self.recommendation_model = None
        self.size_chart_model = None
        
        # Standard size charts (simplified)
        self.size_charts = self._initialize_size_charts()
        
    async def initialize(self):
        """Initialize the size recommender and load AI models"""
        try:
            logger.info("Initializing SizeRecommender...")
            
            # Load AI models (placeholder implementation)
            await self._load_models()
            
            self.models_loaded = True
            logger.info("SizeRecommender initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize SizeRecommender: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            logger.info("Cleaning up SizeRecommender...")
            
            # Cleanup models
            self.recommendation_model = None
            self.size_chart_model = None
            
            logger.info("SizeRecommender cleanup completed")
            
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def get_recommendation(
        self, 
        fit_analysis: FitAnalysis, 
        request: ProcessingRequest
    ) -> SizeRecommendation:
        """
        Get size recommendation based on fit analysis
        
        Args:
            fit_analysis: Results from fit analysis
            request: Original processing request
            
        Returns:
            SizeRecommendation: Size recommendation with confidence and alternatives
        """
        try:
            logger.info(f"Getting size recommendation for request: {request.request_id}")
            
            # Step 1: Analyze current fit
            current_fit_assessment = await self._assess_current_fit(fit_analysis, request)
            
            # Step 2: Determine optimal size
            optimal_size = await self._determine_optimal_size(
                current_fit_assessment, request
            )
            
            # Step 3: Generate alternative sizes
            alternative_sizes = await self._generate_alternative_sizes(
                optimal_size, request
            )
            
            # Step 4: Calculate confidence
            confidence = await self._calculate_recommendation_confidence(
                fit_analysis, current_fit_assessment
            )
            
            # Step 5: Generate fit notes
            fit_notes = await self._generate_fit_notes(
                optimal_size, current_fit_assessment, request
            )
            
            # Create size recommendation
            recommendation = SizeRecommendation(
                recommended_size=optimal_size,
                confidence=confidence,
                alternative_sizes=alternative_sizes,
                fit_notes=fit_notes,
                size_chart=self._get_size_chart(request.garment_type)
            )
            
            logger.info(f"Successfully generated size recommendation for request: {request.request_id}")
            return recommendation
            
        except Exception as e:
            logger.error(f"Error getting size recommendation: {e}")
            raise
    
    # Private helper methods
    
    async def _load_models(self):
        """Load AI models for size recommendation"""
        # Placeholder for actual model loading
        # In a real implementation, this would load:
        # - Size recommendation models
        # - Size chart analysis models
        # - Historical fit data models
        
        logger.info("Loading AI models for size recommendation...")
        
        # Simulate model loading
        await asyncio.sleep(0.1)
        
        logger.info("AI models loaded successfully")
    
    def _initialize_size_charts(self) -> Dict[str, Dict[str, Dict[str, float]]]:
        """Initialize standard size charts for different garment types"""
        # Simplified size charts - in practice, these would be more comprehensive
        # and could be loaded from external sources or databases
        
        size_charts = {
            "shirt": {
                "XS": {"chest": 85, "waist": 70, "length": 65},
                "S": {"chest": 90, "waist": 75, "length": 67},
                "M": {"chest": 95, "waist": 80, "length": 69},
                "L": {"chest": 100, "waist": 85, "length": 71},
                "XL": {"chest": 105, "waist": 90, "length": 73},
                "XXL": {"chest": 110, "waist": 95, "length": 75}
            },
            "pants": {
                "XS": {"waist": 70, "hips": 85, "inseam": 75},
                "S": {"waist": 75, "hips": 90, "inseam": 77},
                "M": {"waist": 80, "hips": 95, "inseam": 79},
                "L": {"waist": 85, "hips": 100, "inseam": 81},
                "XL": {"waist": 90, "hips": 105, "inseam": 83},
                "XXL": {"waist": 95, "hips": 110, "inseam": 85}
            },
            "dress": {
                "XS": {"chest": 85, "waist": 70, "hips": 85, "length": 90},
                "S": {"chest": 90, "waist": 75, "hips": 90, "length": 92},
                "M": {"chest": 95, "waist": 80, "hips": 95, "length": 94},
                "L": {"chest": 100, "waist": 85, "hips": 100, "length": 96},
                "XL": {"chest": 105, "waist": 90, "hips": 105, "length": 98},
                "XXL": {"chest": 110, "waist": 95, "hips": 110, "length": 100}
            }
        }
        
        return size_charts
    
    async def _assess_current_fit(
        self, 
        fit_analysis: FitAnalysis, 
        request: ProcessingRequest
    ) -> Dict[str, Any]:
        """Assess the current fit of the garment"""
        try:
            current_fit = {
                "overall_score": fit_analysis.fit_score,
                "fit_quality": fit_analysis.fit_quality,
                "areas_of_concern": fit_analysis.areas_of_concern,
                "detailed_metrics": fit_analysis.detailed_metrics,
                "measurements": request.user_measurements,
                "garment_type": request.garment_type
            }
            
            return current_fit
            
        except Exception as e:
            logger.error(f"Error assessing current fit: {e}")
            raise
    
    async def _determine_optimal_size(
        self, 
        current_fit: Dict[str, Any], 
        request: ProcessingRequest
    ) -> str:
        """Determine the optimal size for the user"""
        try:
            measurements = request.user_measurements
            garment_type = request.garment_type
            
            # Get size chart for garment type
            size_chart = self.size_charts.get(garment_type, {})
            if not size_chart:
                return "M"  # Default fallback
            
            # Calculate size scores for each available size
            size_scores = {}
            
            for size, size_measurements in size_chart.items():
                score = await self._calculate_size_score(
                    measurements, size_measurements, garment_type
                )
                size_scores[size] = score
            
            # Find the size with the highest score
            if size_scores:
                optimal_size = max(size_scores, key=size_scores.get)
                return optimal_size
            
            return "M"  # Default fallback
            
        except Exception as e:
            logger.error(f"Error determining optimal size: {e}")
            return "M"
    
    async def _calculate_size_score(
        self, 
        user_measurements: UserMeasurements, 
        size_measurements: Dict[str, float], 
        garment_type: str
    ) -> float:
        """Calculate how well a size fits the user"""
        try:
            score = 0.0
            total_weight = 0.0
            
            if garment_type == "shirt":
                # For shirts, prioritize chest and waist
                if "chest" in size_measurements and user_measurements.chest:
                    chest_score = self._calculate_measurement_score(
                        user_measurements.chest, size_measurements["chest"]
                    )
                    score += chest_score * 0.6
                    total_weight += 0.6
                
                if "waist" in size_measurements and user_measurements.waist:
                    waist_score = self._calculate_measurement_score(
                        user_measurements.waist, size_measurements["waist"]
                    )
                    score += waist_score * 0.4
                    total_weight += 0.4
                
            elif garment_type == "pants":
                # For pants, prioritize waist and hips
                if "waist" in size_measurements and user_measurements.waist:
                    waist_score = self._calculate_measurement_score(
                        user_measurements.waist, size_measurements["waist"]
                    )
                    score += waist_score * 0.5
                    total_weight += 0.5
                
                if "hips" in size_measurements and user_measurements.hips:
                    hips_score = self._calculate_measurement_score(
                        user_measurements.hips, size_measurements["hips"]
                    )
                    score += hips_score * 0.5
                    total_weight += 0.5
                
            elif garment_type == "dress":
                # For dresses, consider all measurements
                if "chest" in size_measurements and user_measurements.chest:
                    chest_score = self._calculate_measurement_score(
                        user_measurements.chest, size_measurements["chest"]
                    )
                    score += chest_score * 0.4
                    total_weight += 0.4
                
                if "waist" in size_measurements and user_measurements.waist:
                    waist_score = self._calculate_measurement_score(
                        user_measurements.waist, size_measurements["waist"]
                    )
                    score += waist_score * 0.4
                    total_weight += 0.4
                
                if "hips" in size_measurements and user_measurements.hips:
                    hips_score = self._calculate_measurement_score(
                        user_measurements.hips, size_measurements["hips"]
                    )
                    score += hips_score * 0.2
                    total_weight += 0.2
            
            # Normalize score
            if total_weight > 0:
                return score / total_weight
            
            return 0.5
            
        except Exception as e:
            logger.error(f"Error calculating size score: {e}")
            return 0.5
    
    def _calculate_measurement_score(self, user_value: float, size_value: float) -> float:
        """Calculate how well a specific measurement fits"""
        try:
            # Calculate the ratio between user measurement and size measurement
            ratio = user_value / size_value
            
            # Score based on how close to 1.0 (perfect fit)
            if 0.95 <= ratio <= 1.05:
                return 1.0  # Perfect fit
            elif 0.9 <= ratio <= 1.1:
                return 0.8  # Good fit
            elif 0.85 <= ratio <= 1.15:
                return 0.6  # Acceptable fit
            elif 0.8 <= ratio <= 1.2:
                return 0.4  # Poor fit
            else:
                return 0.2  # Very poor fit
                
        except Exception as e:
            logger.error(f"Error calculating measurement score: {e}")
            return 0.5
    
    async def _generate_alternative_sizes(
        self, 
        optimal_size: str, 
        request: ProcessingRequest
    ) -> List[str]:
        """Generate alternative sizes to try"""
        try:
            alternatives = []
            size_chart = self.size_charts.get(request.garment_type, {})
            
            if not size_chart:
                return alternatives
            
            # Get size order for the garment type
            size_order = list(size_chart.keys())
            
            try:
                current_index = size_order.index(optimal_size)
                
                # Add adjacent sizes
                if current_index > 0:
                    alternatives.append(size_order[current_index - 1])
                if current_index < len(size_order) - 1:
                    alternatives.append(size_order[current_index + 1])
                
                # Add one more size away if available
                if current_index > 1:
                    alternatives.append(size_order[current_index - 2])
                if current_index < len(size_order) - 2:
                    alternatives.append(size_order[current_index + 2])
                
            except ValueError:
                # Optimal size not found in chart
                pass
            
            # Remove duplicates and limit to 3 alternatives
            alternatives = list(set(alternatives))[:3]
            
            return alternatives
            
        except Exception as e:
            logger.error(f"Error generating alternative sizes: {e}")
            return []
    
    async def _calculate_recommendation_confidence(
        self, 
        fit_analysis: FitAnalysis, 
        current_fit: Dict[str, Any]
    ) -> float:
        """Calculate confidence in the size recommendation"""
        try:
            # Base confidence
            base_confidence = 0.7
            
            # Adjust based on fit analysis confidence
            base_confidence += (fit_analysis.confidence - 0.5) * 0.2
            
            # Adjust based on overall fit score
            if current_fit["overall_score"] > 0.8:
                base_confidence += 0.1  # High fit score increases confidence
            elif current_fit["overall_score"] < 0.4:
                base_confidence -= 0.1  # Low fit score decreases confidence
            
            # Adjust based on measurement completeness
            measurements = current_fit["measurements"]
            complete_measurements = sum([
                measurements.chest is not None,
                measurements.waist is not None,
                measurements.hips is not None,
                measurements.shoulder_width is not None
            ])
            
            if complete_measurements >= 4:
                base_confidence += 0.1
            elif complete_measurements <= 2:
                base_confidence -= 0.1
            
            # Ensure confidence is between 0 and 1
            return max(0.0, min(1.0, base_confidence))
            
        except Exception as e:
            logger.error(f"Error calculating recommendation confidence: {e}")
            return 0.5
    
    async def _generate_fit_notes(
        self, 
        optimal_size: str, 
        current_fit: Dict[str, Any], 
        request: ProcessingRequest
    ) -> str:
        """Generate detailed fit notes for the recommendation"""
        try:
            fit_notes = []
            
            # Overall fit assessment
            if current_fit["overall_score"] >= 0.8:
                fit_notes.append(f"Size {optimal_size} provides excellent fit for your measurements")
            elif current_fit["overall_score"] >= 0.6:
                fit_notes.append(f"Size {optimal_size} provides good fit with minor adjustments possible")
            else:
                fit_notes.append(f"Size {optimal_size} is recommended, but consider trying alternatives")
            
            # Specific measurement notes
            measurements = current_fit["measurements"]
            size_chart = self.size_charts.get(request.garment_type, {})
            
            if optimal_size in size_chart:
                size_measurements = size_chart[optimal_size]
                
                if "chest" in size_measurements and measurements.chest:
                    chest_ratio = measurements.chest / size_measurements["chest"]
                    if chest_ratio < 0.9:
                        fit_notes.append("Chest area will have comfortable ease")
                    elif chest_ratio > 1.1:
                        fit_notes.append("Chest area may be snug")
                
                if "waist" in size_measurements and measurements.waist:
                    waist_ratio = measurements.waist / size_measurements["waist"]
                    if waist_ratio < 0.9:
                        fit_notes.append("Waist will have comfortable ease")
                    elif waist_ratio > 1.1:
                        fit_notes.append("Waist area may be snug")
            
            # Fabric-specific notes
            if request.fabric_properties.material == FabricMaterial.COTTON:
                if request.fabric_properties.stretch < 0.1:
                    fit_notes.append("Low-stretch fabric - ensure proper sizing")
                else:
                    fit_notes.append("Fabric has some stretch for comfort")
            
            # Garment type specific notes
            if request.garment_type == "shirt":
                fit_notes.append("Consider sleeve length for your arm measurements")
            elif request.garment_type == "pants":
                fit_notes.append("Check inseam length for your height")
            
            # Combine notes
            if fit_notes:
                return " ".join(fit_notes)
            else:
                return f"Size {optimal_size} is recommended based on your measurements"
                
        except Exception as e:
            logger.error(f"Error generating fit notes: {e}")
            return f"Size {optimal_size} is recommended"
    
    def _get_size_chart(self, garment_type: str) -> Optional[Dict[str, Any]]:
        """Get size chart for the garment type"""
        try:
            return self.size_charts.get(garment_type, None)
        except Exception as e:
            logger.error(f"Error getting size chart: {e}")
            return None
