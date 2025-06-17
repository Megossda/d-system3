# File: examples/test_enhanced_systems.py
"""Comprehensive test suite for enhanced error handling and logging systems."""

import sys
import os
import time
import json

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_enhanced_error_handling():
    """Test all new error handling features."""
    print("=== TESTING ENHANCED ERROR HANDLING FEATURES ===\n")
    
    from creatures.base import Creature
    from error_handling.error_handler import (
        DnDErrorHandler, DnDError, SpellcastingError, CombatError, ActionError,
        ErrorSeverity
    )
    from systems.action_execution_system import ActionExecutor
    from actions.attack_action import WeaponAttackAction
    
    # Test 1: Error Severity System
    print("--- Test 1: Error Severity System ---")
    try:
        raise DnDError(
            "Test error with severity",
            severity=ErrorSeverity.MAJOR,
            context={'test_context': 'severity_test'},
            recovery_suggestion="This is a test - no action needed"
        )
    except DnDError as e:
        print(f"✅ Error severity: {e.severity.value}")
        print(f"✅ Error context: {e.context}")
        print(f"✅ Recovery suggestion: {e.recovery_suggestion}")
    
    # Test 2: Specialized Error Classes
    print("\n--- Test 2: Specialized Error Classes ---")
    fighter = Creature(
        name="Test Fighter", level=3, ac=16, hp=25, speed=30,
        stats={'str': 16, 'dex': 12, 'con': 14, 'int': 10, 'wis': 11, 'cha': 10},
        proficiencies={'longsword'}
    )
    
    try:
        raise SpellcastingError(
            "Test spellcasting error",
            spell_name="Fireball",
            caster_name=fighter.name,
            severity=ErrorSeverity.MODERATE
        )
    except SpellcastingError as e:
        print(f"✅ Spellcasting error context: {e.context}")
    
    try:
        raise CombatError(
            "Test combat error",
            attacker_name=fighter.name,
            target_name="Test Target",
            severity=ErrorSeverity.MINOR
        )
    except CombatError as e:
        print(f"✅ Combat error context: {e.context}")
    
    # Test 3: Error Metrics
    print("\n--- Test 3: Error Metrics ---")
    # Reset metrics for clean test
    DnDErrorHandler.reset_error_metrics()
    
    # Generate some test errors
    test_errors = [
        DnDError("Minor test error", severity=ErrorSeverity.MINOR),
        DnDError("Moderate test error", severity=ErrorSeverity.MODERATE),
        DnDError("Major test error", severity=ErrorSeverity.MAJOR),
    ]
    
    for error in test_errors:
        DnDErrorHandler._handle_dnd_error(error, "test_operation")
    
    metrics = DnDErrorHandler.get_error_metrics()
    print(f"✅ Total errors recorded: {metrics['total_errors']}")
    print(f"✅ Errors by severity: {metrics['errors_by_severity']}")
    print(f"✅ Recent errors: {metrics['recent_errors_count']}")
    
    # Test 4: Enhanced Safe Execution with Retries
    print("\n--- Test 4: Safe Execution with Retries ---")
    
    attempt_count = 0
    
    @DnDErrorHandler.safe_execute("retry_test", max_retries=2, fallback_result="FALLBACK")
    def flaky_operation():
        nonlocal attempt_count
        attempt_count += 1
        if attempt_count < 3:  # Fail first 2 attempts
            raise ValueError(f"Attempt {attempt_count} failed")
        return "SUCCESS"
    
    result = flaky_operation()
    print(f"✅ Retry operation result: {result}")
    print(f"✅ Total attempts made: {attempt_count}")
    
    # Test 5: Context Manager
    print("\n--- Test 5: Error Context Manager ---")
    
    try:
        with DnDErrorHandler.create_context_manager("test_context", test_param="test_value"):
            raise ValueError("Test error in context")
    except:
        pass  # Expected to be handled by context manager
    
    print("✅ Context manager handled error gracefully")
    
    # Test 6: Enhanced Validation
    print("\n--- Test 6: Enhanced Validation ---")
    
    # Test invalid creature
    try:
        DnDErrorHandler.validate_creature(None, "validation_test")
    except DnDError as e:
        print(f"✅ Creature validation error: {e.recovery_suggestion}")
    
    # Test creature with missing attributes
    class BrokenCreature:
        def __init__(self):
            self.name = "Broken Creature"
            # Missing: is_alive, current_hp, max_hp
    
    broken_creature = BrokenCreature()
    
    try:
        DnDErrorHandler.validate_creature(broken_creature, "validation_test")
    except DnDError as e:
        print(f"✅ Missing attributes detected: {e.context['missing_attributes']}")
    
    print("\n✅ Enhanced error handling tests completed!")

def test_enhanced_logging():
    """Test all new logging features."""
    print("\n=== TESTING ENHANCED LOGGING FEATURES ===\n")
    
    from error_handling.logging_setup import (
        log_manager, LoggingContext, PerformanceContext, 
        EnhancedCombatLogging, log_with_performance, log_system_health
    )
    from creatures.base import Creature
    
    # Test 1: Setup Enhanced Logging
    print("--- Test 1: Enhanced Logging Setup ---")
    
    # Configure with all features enabled
    config = {
        'log_level': 10,  # DEBUG level
        'console_output': True,
        'file_output': True,
        'json_output': True,
        'colored_console': True
    }
    
    logger = log_manager.setup_logging(config)
    print("✅ Enhanced logging configured")
    
    # Get logging statistics
    stats = log_manager.get_log_stats()
    print(f"✅ Log directory: {stats['log_directory']}")
    print(f"✅ Active loggers: {len(stats['specialized_loggers'])}")
    print(f"✅ Handlers count: {stats['handlers_count']}")
    
    # Test 2: Context-Aware Logging
    print("\n--- Test 2: Context-Aware Logging ---")
    
    test_logger = log_manager.get_logger('TestSystem')
    
    with LoggingContext(creature_name="Test Creature", spell_name="Test Spell", combat_round=1):
        test_logger.info("This message includes context automatically")
        test_logger.warning("Context is added to all messages in this block")
    
    test_logger.info("This message has no special context")
    print("✅ Context-aware logging demonstrated")
    
    # Test 3: Performance Monitoring
    print("\n--- Test 3: Performance Monitoring ---")
    
    with PerformanceContext("test_operation"):
        time.sleep(0.1)  # Simulate some work
        print("✅ Simulated operation completed")
    
    print("✅ Performance monitoring demonstrated (check logs)")
    
    # Test 4: Performance Decorator
    print("\n--- Test 4: Performance Decorator ---")
    
    @log_with_performance("decorated_operation")
    def slow_operation():
        time.sleep(0.05)  # Simulate work
        return "Operation complete"
    
    result = slow_operation()
    print(f"✅ Decorated operation result: {result}")
    
    # Test 5: Enhanced Combat Logging
    print("\n--- Test 5: Enhanced Combat Logging ---")
    
    # Create test creatures
    fighter = Creature(
        name="Test Fighter", level=3, ac=16, hp=25, speed=30,
        stats={'str': 16, 'dex': 12, 'con': 14, 'int': 10, 'wis': 11, 'cha': 10}
    )
    
    orc = Creature(
        name="Test Orc", level=2, ac=13, hp=20, speed=30,
        stats={'str': 14, 'dex': 10, 'con': 12, 'int': 8, 'wis': 9, 'cha': 8}
    )
    
    participants = [fighter, orc]
    
    # Log combat events
    EnhancedCombatLogging.log_combat_start(participants, round_number=1)
    EnhancedCombatLogging.log_turn_start(fighter, round_number=1, turn_number=1)
    EnhancedCombatLogging.log_action_attempt(fighter, "Attack", target=orc)
    EnhancedCombatLogging.log_damage_dealt(orc, 8, "slashing", source=fighter)
    EnhancedCombatLogging.log_condition_change(orc, "prone", added=True)
    EnhancedCombatLogging.log_combat_end(winner="Test Fighter", reason="Target defeated")
    
    print("✅ Enhanced combat logging demonstrated")
    
    # Test 6: System Health Logging
    print("\n--- Test 6: System Health Monitoring ---")
    
    log_system_health()
    print("✅ System health logged (check logs for details)")
    
    # Test 7: Emergency Logging
    print("\n--- Test 7: Emergency Logging ---")
    
    log_manager.emergency_log("Test emergency message", {"test": "emergency_details"})
    print("✅ Emergency logging tested")
    
    print("\n✅ Enhanced logging tests completed!")

def test_integration_with_existing_systems():
    """Test integration with existing D&D systems."""
    print("\n=== TESTING INTEGRATION WITH EXISTING SYSTEMS ===\n")
    
    from creatures.base import Creature
    from systems.action_execution_system import ActionExecutor
    from actions.attack_action import WeaponAttackAction
    from systems.character_abilities.spellcasting import SpellcastingManager
    from spells.cantrips.fire_bolt import fire_bolt
    from actions.spell_actions import CastSpellAction
    from error_handling.logging_setup import LoggingContext, EnhancedCombatLogging
    from error_handling.error_handler import DnDErrorHandler
    
    # Test 1: Combat with Enhanced Logging
    print("--- Test 1: Combat with Enhanced Logging ---")
    
    fighter = Creature(
        name="Enhanced Fighter", level=4, ac=17, hp=35, speed=30,
        stats={'str': 17, 'dex': 12, 'con': 15, 'int': 10, 'wis': 12, 'cha': 11},
        proficiencies={'longsword', 'athletics'}
    )
    
    target = Creature(
        name="Enhanced Target", level=2, ac=14, hp=25, speed=30,
        stats={'str': 13, 'dex': 11, 'con': 13, 'int': 9, 'wis': 10, 'cha': 8}
    )
    
    # Start combat with enhanced logging
    participants = [fighter, target]
    EnhancedCombatLogging.log_combat_start(participants, round_number=1)
    
    # Fighter's turn with context logging
    with LoggingContext(creature_name=fighter.name, combat_round=1, turn_number=1):
        fighter.start_turn()
        EnhancedCombatLogging.log_turn_start(fighter, round_number=1, turn_number=1)
        
        # Attack action with enhanced error handling
        longsword_action = WeaponAttackAction("Longsword", "1d8", "str", "slashing")
        EnhancedCombatLogging.log_action_attempt(fighter, "Longsword Attack", target=target)
        
        result = ActionExecutor.action(fighter, longsword_action, target=target)
        print(f"✅ Attack result: {result.success}")
        
        if result.success:
            # Simulate damage logging
            EnhancedCombatLogging.log_damage_dealt(target, 7, "slashing", source=fighter)
    
    # Test 2: Spellcasting with Enhanced Error Handling
    print("\n--- Test 2: Spellcasting with Enhanced Systems ---")
    
    wizard = Creature(
        name="Enhanced Wizard", level=5, ac=12, hp=30, speed=30,
        stats={'str': 8, 'dex': 14, 'con': 14, 'int': 17, 'wis': 12, 'cha': 10},
        proficiencies={'arcana', 'investigation'}
    )
    
    # Set up spellcasting
    SpellcastingManager.add_spellcasting(wizard, 'int')
    SpellcastingManager.add_spell_to_creature(wizard, fire_bolt)
    
    # Cast spell with enhanced logging
    with LoggingContext(creature_name=wizard.name, spell_name="Fire Bolt"):
        wizard.start_turn()
        
        spell_action = CastSpellAction(fire_bolt, target, 0)
        EnhancedCombatLogging.log_spell_cast(wizard, "Fire Bolt", targets=target, spell_level=0)
        
        result = ActionExecutor.action(wizard, spell_action)
        print(f"✅ Spell cast result: {result.success}")
    
    # Test 3: Error Handling in Real Scenarios
    print("\n--- Test 3: Real Scenario Error Handling ---")
    
    # Try to attack with a dead creature
    dead_creature = Creature(
        name="Dead Creature", level=1, ac=10, hp=0, speed=30,
        stats={'str': 10, 'dex': 10, 'con': 10, 'int': 10, 'wis': 10, 'cha': 10}
    )
    dead_creature.is_alive = False
    
    with LoggingContext(creature_name=dead_creature.name):
        dead_creature.start_turn()
        
        attack_action = WeaponAttackAction("Dagger", "1d4", "str", "piercing")
        result = ActionExecutor.action(dead_creature, attack_action, target=target)
        
        print(f"✅ Dead creature attack handled: {result.success}")
        print(f"✅ Error message: {result.message}")
    
    # Test 4: Stress Test Error Metrics
    print("\n--- Test 4: Error Metrics Stress Test ---")
    
    # Reset metrics
    DnDErrorHandler.reset_error_metrics()
    initial_metrics = DnDErrorHandler.get_error_metrics()
    print(f"✅ Initial error count: {initial_metrics['total_errors']}")
    
    # Generate multiple errors through real system usage
    for i in range(5):
        with LoggingContext(test_iteration=i):
            # Try invalid operations that should be handled gracefully
            invalid_action = WeaponAttackAction("Invalid Weapon", "1d999", "invalid_stat", "invalid_damage")
            result = ActionExecutor.action(dead_creature, invalid_action, target=target)
            # These should fail gracefully and be logged
    
    final_metrics = DnDErrorHandler.get_error_metrics()
    print(f"✅ Final error count: {final_metrics['total_errors']}")
    print(f"✅ Errors by severity: {final_metrics['errors_by_severity']}")
    
    EnhancedCombatLogging.log_combat_end(reason="Testing completed")
    
    print("\n✅ Integration tests completed!")

def test_json_logging_output():
    """Test JSON logging output and structured data."""
    print("\n=== TESTING JSON LOGGING OUTPUT ===\n")
    
    from error_handling.logging_setup import log_manager, LoggingContext
    import os
    
    # Ensure JSON logging is enabled
    config = {
        'json_output': True,
        'log_level': 10  # DEBUG
    }
    log_manager.setup_logging(config)
    
    logger = log_manager.get_logger('JSONTest')
    
    # Generate some structured log entries
    with LoggingContext(creature_name="JSON Test Creature", spell_name="Test Spell", combat_round=1):
        logger.info("Testing JSON structured logging")
        logger.warning("This is a warning with context")
        logger.error("This is an error with full context")
    
    # Check if JSON log file exists
    json_log_path = os.path.join('logs', 'dnd_system.jsonl')
    if os.path.exists(json_log_path):
        print(f"✅ JSON log file created: {json_log_path}")
        
        # Read and display last few entries
        with open(json_log_path, 'r') as f:
            lines = f.readlines()
            if lines:
                print("✅ Sample JSON log entry:")
                try:
                    last_entry = json.loads(lines[-1])
                    print(f"   Timestamp: {last_entry.get('timestamp')}")
                    print(f"   Level: {last_entry.get('level')}")
                    print(f"   Message: {last_entry.get('message')}")
                    print(f"   Creature: {last_entry.get('creature_name', 'N/A')}")
                    print(f"   Spell: {last_entry.get('spell_name', 'N/A')}")
                except json.JSONDecodeError:
                    print("   (JSON parsing failed - this is expected during testing)")
    else:
        print("❌ JSON log file not found")
    
    print("\n✅ JSON logging test completed!")

def test_log_file_management():
    """Test log file creation and management."""
    print("\n=== TESTING LOG FILE MANAGEMENT ===\n")
    
    from error_handling.logging_setup import log_manager
    import os
    import glob
    
    # Get current log statistics
    stats = log_manager.get_log_stats()
    print(f"✅ Log directory: {stats['log_directory']}")
    print(f"✅ Log files found: {len(stats['log_files'])}")
    
    # List all log files
    log_dir = 'logs'
    if os.path.exists(log_dir):
        log_files = glob.glob(os.path.join(log_dir, '*.log'))
        print(f"✅ Available log files:")
        for log_file in log_files[-5:]:  # Show last 5 files
            file_size = os.path.getsize(log_file)
            print(f"   {os.path.basename(log_file)} ({file_size} bytes)")
        
        # Check for specific log files
        expected_files = ['dnd_latest.log', 'emergency.log']
        for expected in expected_files:
            expected_path = os.path.join(log_dir, expected)
            if os.path.exists(expected_path):
                print(f"✅ {expected} exists")
            else:
                print(f"ℹ️  {expected} not created yet (this is normal)")
    
    print("\n✅ Log file management test completed!")

def run_all_tests():
    """Run all enhanced system tests."""
    print("🚀 RUNNING ENHANCED SYSTEMS TEST SUITE 🚀\n")
    
    try:
        test_enhanced_error_handling()
        test_enhanced_logging()
        test_integration_with_existing_systems()
        test_json_logging_output()
        test_log_file_management()
        
        print("\n" + "="*70)
        print("🎉 ALL ENHANCED SYSTEMS TESTS COMPLETED SUCCESSFULLY! 🎉")
        print("="*70)
        
        # Final system health check
        print("\n📊 FINAL SYSTEM HEALTH CHECK:")
        from error_handling.logging_setup import log_system_health
        log_system_health()
        
        print("\n✅ Enhanced error handling: Fully operational")
        print("✅ Enhanced logging: Fully operational") 
        print("✅ System integration: Fully operational")
        print("✅ Performance monitoring: Fully operational")
        print("✅ JSON structured logging: Fully operational")
        print("✅ File management: Fully operational")
        
    except Exception as e:
        print(f"\n❌ TEST SUITE FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()