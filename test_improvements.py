"""
Test the improved repo analysis
"""
import asyncio
from tools import analyze_specific_repo_enhanced

async def test_improvements():
    print("🧪 Testing improved repo analysis...")
    
    try:
        result = await analyze_specific_repo_enhanced('Lightly-GPT')
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
            return
        
        print("✅ Analysis completed!")
        print(f"📁 Repo: {result['basic_info']['name']}")
        
        # Quality metrics
        quality = result['quality_metrics']
        print(f"\n🔍 Quality Metrics:")
        print(f"  • Tests: {'✅' if quality['has_tests'] else '❌'}")
        print(f"  • CI/CD: {'✅' if quality['has_ci'] else '❌'}")
        print(f"  • License: {'✅' if quality['has_license'] else '❌'}")
        print(f"  • Quality Score: {quality['quality_score']}/100")
        
        # README analysis
        readme = result['readme']
        print(f"\n📚 README Analysis:")
        print(f"  • Length: {readme['readme_length']} characters")
        print(f"  • Quality: {readme['readme_quality']}")
        print(f"  • Has Installation: {'✅' if readme['has_installation'] else '❌'}")
        print(f"  • Has Usage: {'✅' if readme['has_usage'] else '❌'}")
        print(f"  • Sections: {readme['sections_found']}")
        
        # Overall
        print(f"\n⭐ Overall Score: {result['overall_score']}/100")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_improvements())
