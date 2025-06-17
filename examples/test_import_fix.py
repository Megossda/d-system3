# File: examples/test_import_fix.py
"""Quick test to verify the import fix works."""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_imports():
    """Test that all enhanced imports work correctly."""
    print("🔧 TESTING ENHANCED SYSTEM IMPORTS 🔧\n")
    
    try:
        print("--- Testing Enhanced Error Handler Imports ---")
        from error_handling.error_handler import (
            DnDErrorHandler, DnDError, ErrorSeverity,
            SpellcastingError, CombatError, ActionError
        )
        print("✅ Enhanced error handler imports successful")
        
        print("\n--- Testing Enhanced Logging Imports ---")
        from error_handling.logging_setup import (
            log_manager, LoggingContext, PerformanceContext,
            EnhancedCombatLogging, log_with_performance
        )
        print("✅ Enhanced logging imports successful")
        
        print("\n--- Testing Decorator Functionality ---")
        
        @log_with_performance("test_decorator")
        def test_function():
            import time
            time.sleep(0.01)
            return "Success"
        
        result = test_function()
        print(f"✅ Decorator test result: {result}")
        
        print("\n--- Testing Error Severity ---")
        try:
            raise DnDError(
                "Test error",
                severity=ErrorSeverity.MINOR,
                recovery_suggestion="This is just a test"
            )
        except DnDError as e:
            print(f"✅ Error severity: {e.severity.value}")
            print(f"✅ Recovery: {e.recovery_suggestion}")
        
        print("\n--- Testing Context Logging ---")
        logger = log_manager.get_logger('ImportTest')
        
        with LoggingContext(test_phase="import_verification"):
            logger.info("Import test successful with context")
        
        print("✅ Context logging working")
        
        print("\n--- Testing Performance Context ---")
        
        with PerformanceContext("import_test_operation"):
            import time
            time.sleep(0.005)
            print("✅ Performance context working")
        
        print("\n🎉 ALL IMPORTS AND FEATURES WORKING CORRECTLY! 🎉")
        print("\nYou can now run the full enhanced test suite:")
        print("  python examples/test_enhanced_systems.py")
        print("  python examples/test_enhanced_quick.py")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all enhanced files are properly saved")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == "__main__":
    success = test_imports()
    if success:
        print("\n✅ Ready to run enhanced test suites!")
    else:
        print("\n❌ Please fix import issues before running full tests")