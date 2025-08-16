#!/usr/bin/env python3
"""
Example usage of the AipetAgent for pet care recommendations.

This script demonstrates how to use the pydantic_ai agent to get
intelligent recommendations for pet care based on current needs.

Note: This example uses OpenRouter configuration. Make sure to set up
your OPENROUTER_API_KEY in the environment variables.
"""

import asyncio
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from apps.aipet.agents.aipet_agent import AipetAgent, PetNeeds


async def main():
    """Main function demonstrating agent usage."""
    
    print("🐾 AIPet Agent Example (OpenRouter)")
    print("=" * 50)
    
    # Initialize the agent (will use default model from config)
    agent = AipetAgent()
    
    # Example 1: Very hungry pet
    print("\n📋 Example 1: Very Hungry Pet")
    print("-" * 30)
    
    hungry_pet = PetNeeds(
        hungry=95,      # Very hungry
        tiredness=20,   # Not tired
        boredom=30,     # Slightly bored
        toilet=40       # Moderate toilet need
    )
    
    print(f"Pet needs: {hungry_pet}")
    
    try:
        recommendations = await agent.get_recommendations(hungry_pet)
        
        print(f"\n🎯 Primary Action: {recommendations.primary_action.action}")
        print(f"   Priority: {recommendations.primary_action.priority}/5")
        print(f"   Reasoning: {recommendations.primary_action.reasoning}")
        print(f"   Target Need: {recommendations.primary_action.target_need}")
        print(f"   Estimated Effect: {recommendations.primary_action.estimated_effect}%")
        
        if recommendations.secondary_actions:
            print(f"\n📝 Secondary Actions:")
            for i, action in enumerate(recommendations.secondary_actions, 1):
                print(f"   {i}. {action.action} (Priority: {action.priority}/5)")
        
        print(f"\n🏥 Overall Health Score: {recommendations.overall_health_score}/100")
        print(f"🚨 Urgent Needs: {', '.join(recommendations.urgent_needs)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 2: Tired pet
    print("\n\n📋 Example 2: Tired Pet")
    print("-" * 30)
    
    tired_pet = PetNeeds(
        hungry=30,      # Not very hungry
        tiredness=85,   # Very tired
        boredom=60,     # Moderately bored
        toilet=25       # Low toilet need
    )
    
    print(f"Pet needs: {tired_pet}")
    
    try:
        recommendations = await agent.get_recommendations(tired_pet)
        
        print(f"\n🎯 Primary Action: {recommendations.primary_action.action}")
        print(f"   Priority: {recommendations.primary_action.priority}/5")
        print(f"   Reasoning: {recommendations.primary_action.reasoning}")
        print(f"   Target Need: {recommendations.primary_action.target_need}")
        print(f"   Estimated Effect: {recommendations.primary_action.estimated_effect}%")
        
        if recommendations.secondary_actions:
            print(f"\n📝 Secondary Actions:")
            for i, action in enumerate(recommendations.secondary_actions, 1):
                print(f"   {i}. {action.action} (Priority: {action.priority}/5)")
        
        print(f"\n🏥 Overall Health Score: {recommendations.overall_health_score}/100")
        print(f"🚨 Urgent Needs: {', '.join(recommendations.urgent_needs)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Example 3: Well-balanced pet
    print("\n\n📋 Example 3: Well-Balanced Pet")
    print("-" * 30)
    
    balanced_pet = PetNeeds(
        hungry=25,      # Slightly hungry
        tiredness=35,   # Slightly tired
        boredom=20,     # Not bored
        toilet=15       # Low toilet need
    )
    
    print(f"Pet needs: {balanced_pet}")
    
    try:
        recommendations = await agent.get_recommendations(balanced_pet)
        
        print(f"\n🎯 Primary Action: {recommendations.primary_action.action}")
        print(f"   Priority: {recommendations.primary_action.priority}/5")
        print(f"   Reasoning: {recommendations.primary_action.reasoning}")
        print(f"   Target Need: {recommendations.primary_action.target_need}")
        print(f"   Estimated Effect: {recommendations.primary_action.estimated_effect}%")
        
        if recommendations.secondary_actions:
            print(f"\n📝 Secondary Actions:")
            for i, action in enumerate(recommendations.secondary_actions, 1):
                print(f"   {i}. {action.action} (Priority: {action.priority}/5)")
        
        print(f"\n🏥 Overall Health Score: {recommendations.overall_health_score}/100")
        print(f"🚨 Urgent Needs: {', '.join(recommendations.urgent_needs)}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("✨ Example completed!")


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main()) 