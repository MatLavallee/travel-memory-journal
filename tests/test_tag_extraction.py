"""Test Travel Memory Journal tag extraction service."""

import pytest
from ai_journaling_assistant.tag_extraction import TagExtractor


class TestTagExtractor:
    """Test tag extraction service initialization."""

    def test_tag_extractor_initialization(self):
        """Initializes with travel-specific keyword dictionaries."""
        extractor = TagExtractor()
        
        assert hasattr(extractor, 'categories')
        assert isinstance(extractor.categories, dict)
        assert "food" in extractor.categories
        assert "culture" in extractor.categories


class TestTagExtractionFood:
    """Test food-related tag extraction."""

    def test_tag_extraction_food_keywords(self):
        """Extracts food-related tags from descriptions."""
        extractor = TagExtractor()
        
        description = "Had amazing pasta at a local restaurant and great wine"
        tags = extractor.extract_tags(description)
        
        # Should contain food-related tags
        food_tags = [tag for tag in tags if tag in extractor.categories["food"]]
        assert len(food_tags) > 0
        assert "restaurant" in tags
        assert "wine" in tags

    def test_tag_extraction_coffee_culture(self):
        """Identifies coffee and cafe culture tags."""
        extractor = TagExtractor()
        
        description = "Started the morning with coffee at a charming cafe"
        tags = extractor.extract_tags(description)
        
        assert "coffee" in tags
        assert "cafe" in tags

    def test_tag_extraction_market_food(self):
        """Extracts market and local food tags."""
        extractor = TagExtractor()
        
        description = "Explored the local market and tried street food"
        tags = extractor.extract_tags(description)
        
        assert "market" in tags
        assert "street food" in tags


class TestTagExtractionCulture:
    """Test culture-related tag extraction."""

    def test_tag_extraction_culture_keywords(self):
        """Identifies cultural activity tags."""
        extractor = TagExtractor()
        
        description = "Visited the museum and saw incredible art and architecture"
        tags = extractor.extract_tags(description)
        
        culture_tags = [tag for tag in tags if tag in extractor.categories["culture"]]
        assert len(culture_tags) > 0
        assert "museum" in tags
        assert "art" in tags
        assert "architecture" in tags

    def test_tag_extraction_temple_heritage(self):
        """Extracts temple and heritage site tags."""
        extractor = TagExtractor()
        
        description = "Explored ancient temple with rich history and traditional ceremony"
        tags = extractor.extract_tags(description)
        
        assert "temple" in tags
        assert "history" in tags
        assert "traditional" in tags


class TestTagExtractionOutdoor:
    """Test outdoor activity tag extraction."""

    def test_tag_extraction_outdoor_activities(self):
        """Extracts outdoor and nature activity tags."""
        extractor = TagExtractor()
        
        description = "Went hiking in the mountains and enjoyed beautiful nature"
        tags = extractor.extract_tags(description)
        
        outdoor_tags = [tag for tag in tags if tag in extractor.categories["outdoor"]]
        assert len(outdoor_tags) > 0
        assert "hiking" in tags
        assert "mountain" in tags
        assert "nature" in tags

    def test_tag_extraction_beach_activities(self):
        """Identifies beach and water activity tags."""
        extractor = TagExtractor()
        
        description = "Relaxing day at the beach with swimming and surfing"
        tags = extractor.extract_tags(description)
        
        assert "beach" in tags
        assert "swimming" in tags
        assert "surfing" in tags


class TestTagExtractionTransport:
    """Test transportation tag extraction."""

    def test_tag_extraction_transport_methods(self):
        """Extracts transportation method tags."""
        extractor = TagExtractor()
        
        description = "Took the train to the city, then used metro and walked around"
        tags = extractor.extract_tags(description)
        
        transport_tags = [tag for tag in tags if tag in extractor.categories["transport"]]
        assert len(transport_tags) > 0
        assert "train" in tags
        assert "metro" in tags
        assert "walking" in tags


class TestTagExtractionAccommodation:
    """Test accommodation tag extraction."""

    def test_tag_extraction_accommodation_types(self):
        """Extracts accommodation type tags."""
        extractor = TagExtractor()
        
        description = "Stayed at a lovely hotel near the city center"
        tags = extractor.extract_tags(description)
        
        accommodation_tags = [tag for tag in tags if tag in extractor.categories["accommodation"]]
        assert len(accommodation_tags) > 0
        assert "hotel" in tags

    def test_tag_extraction_airbnb_accommodation(self):
        """Identifies alternative accommodation tags."""
        extractor = TagExtractor()
        
        description = "Booked an airbnb apartment for our stay"
        tags = extractor.extract_tags(description)
        
        assert "airbnb" in tags
        assert "apartment" in tags


class TestTagExtractionMixed:
    """Test mixed content tag extraction."""

    def test_tag_extraction_mixed_content(self):
        """Handles descriptions with multiple categories."""
        extractor = TagExtractor()
        
        description = """Today I visited Paris, went to a restaurant, had coffee, 
        some good wine from Beaujolais, visited the Louvre museum, saw the Mona Lisa, 
        then went to the mountain, did some skiing and shopping at local market."""
        
        tags = extractor.extract_tags(description)
        
        # Should contain tags from multiple categories
        assert "restaurant" in tags  # food
        assert "coffee" in tags      # food
        assert "wine" in tags        # food
        assert "museum" in tags      # culture (Louvre)
        assert "mountain" in tags    # outdoor
        assert "market" in tags      # shopping/food

    def test_tag_extraction_complex_travel_day(self):
        """Extracts tags from complex multi-activity description."""
        extractor = TagExtractor()
        
        description = """Amazing day in Tokyo! Started with breakfast at hotel, 
        took the train to visit temple, had sushi for lunch, explored art gallery, 
        went shopping in evening, then enjoyed nightlife at local bar."""
        
        tags = extractor.extract_tags(description)
        
        # Multiple categories should be represented
        food_tags = [tag for tag in tags if tag in extractor.categories["food"]]
        culture_tags = [tag for tag in tags if tag in extractor.categories["culture"]]
        transport_tags = [tag for tag in tags if tag in extractor.categories["transport"]]
        
        assert len(food_tags) > 0
        assert len(culture_tags) > 0
        assert len(transport_tags) > 0


class TestTagExtractionEdgeCases:
    """Test edge cases and error handling."""

    def test_tag_extraction_no_matches(self):
        """Returns empty list when no keywords found."""
        extractor = TagExtractor()
        
        description = "This description contains no travel keywords whatsoever"
        tags = extractor.extract_tags(description)
        
        assert isinstance(tags, list)
        assert len(tags) == 0

    def test_tag_extraction_case_insensitive(self):
        """Works regardless of text case."""
        extractor = TagExtractor()
        
        description = "VISITED MUSEUM AND ART GALLERY"
        tags = extractor.extract_tags(description)
        
        assert "museum" in tags
        assert "art" in tags

    def test_tag_extraction_empty_description(self):
        """Handles empty description gracefully."""
        extractor = TagExtractor()
        
        tags = extractor.extract_tags("")
        
        assert isinstance(tags, list)
        assert len(tags) == 0

    def test_tag_extraction_punctuation_handling(self):
        """Handles punctuation and special characters."""
        extractor = TagExtractor()
        
        description = "Great restaurant! Amazing wine... Beautiful art, incredible museum."
        tags = extractor.extract_tags(description)
        
        assert "restaurant" in tags
        assert "wine" in tags
        assert "art" in tags
        assert "museum" in tags

    def test_tag_extraction_duplicate_removal(self):
        """Removes duplicate tags from result."""
        extractor = TagExtractor()
        
        description = "Restaurant food at restaurant with restaurant atmosphere"
        tags = extractor.extract_tags(description)
        
        # Should only contain "restaurant" once
        restaurant_count = tags.count("restaurant")
        assert restaurant_count == 1

    def test_tag_extraction_partial_word_matching(self):
        """Handles partial word matches appropriately."""
        extractor = TagExtractor()
        
        description = "Restaurateur served food at the restaurant"
        tags = extractor.extract_tags(description)
        
        # Should match "restaurant" but not be confused by "restaurateur"
        assert "restaurant" in tags


class TestTagExtractionCategorization:
    """Test tag categorization functionality."""

    def test_tag_extraction_with_categories(self):
        """Returns tags organized by category when requested."""
        extractor = TagExtractor()
        
        description = "Had sushi at restaurant, visited temple, went hiking"
        categorized_tags = extractor.extract_tags_by_category(description)
        
        assert isinstance(categorized_tags, dict)
        assert "food" in categorized_tags
        assert "culture" in categorized_tags
        assert "outdoor" in categorized_tags
        
        assert "restaurant" in categorized_tags["food"]
        assert "temple" in categorized_tags["culture"]
        assert "hiking" in categorized_tags["outdoor"]

    def test_tag_extraction_category_filtering(self):
        """Filters tags by specific categories."""
        extractor = TagExtractor()
        
        description = "Restaurant meal, museum visit, hiking trip"
        food_tags = extractor.extract_tags(description, categories=["food"])
        
        assert "restaurant" in food_tags
        assert "museum" not in food_tags  # Should be filtered out
        assert "hiking" not in food_tags  # Should be filtered out


class TestTagExtractionPerformance:
    """Test tag extraction performance requirements."""

    def test_tag_extraction_performance(self):
        """Processes descriptions quickly for performance requirements."""
        extractor = TagExtractor()
        
        # Long description to test performance
        description = """
        Amazing 2-week trip across Europe! Started in Paris with incredible 
        restaurant experiences, visited Louvre museum, took train to Rome, 
        explored Colosseum and Vatican, had amazing pasta and wine, flew to 
        Barcelona, saw Gaudi architecture, went to beaches, took bus to Madrid, 
        visited Prado museum, enjoyed tapas and local markets, trained to 
        Amsterdam, cycled through city, visited Van Gogh museum, stayed at 
        boutique hotel, final flight to London, explored British Museum, 
        had afternoon tea, walked through parks, took underground everywhere.
        """ * 5  # Repeat to make it longer
        
        import time
        start_time = time.time()
        tags = extractor.extract_tags(description)
        end_time = time.time()
        
        # Should complete within reasonable time (< 1 second for this test)
        processing_time = end_time - start_time
        assert processing_time < 1.0
        
        # Should still extract meaningful tags
        assert len(tags) > 10
        assert "restaurant" in tags
        assert "museum" in tags