# File: actions/insight_action.py
"""Implementation of the Insight action for reading NPCs."""
from systems.d20_system import perform_d20_test

class InsightAction:
    """Represents making an Insight check to read NPCs and situations."""
    def __init__(self):
        self.name = "Insight"

    def execute(self, performer, target=None, dc_to_beat=15):
        """
        The performer makes a Wisdom (Insight) check to read someone's intentions.
        NOTE: Action economy is handled by ActionExecutionSystem, not here.
        """
        if target:
            print(f"  > {performer.name} studies {target.name}, trying to read their intentions...")
        else:
            print(f"  > {performer.name} tries to gain insight into the situation...")
        
        # Make a Wisdom (Insight) check
        was_successful = perform_d20_test(
            creature=performer,
            ability_name='wis',
            check_type='insight',
            dc=dc_to_beat
        )
        
        if was_successful:
            if target:
                # Reveal information about the target's emotional state
                self._reveal_npc_insights(performer, target)
            else:
                print(f"  > {performer.name} gains valuable insight into the situation!")
        else:
            print(f"  > {performer.name} cannot read the situation clearly.")

        return was_successful
    
    def _reveal_npc_insights(self, performer, target):
        """Reveal insights about the target NPC based on their state."""
        insights = []
        
        # Check target's attitude
        if target.attitude == 'Hostile':
            insights.append("they seem hostile and aggressive")
        elif target.attitude == 'Friendly':
            insights.append("they appear genuinely friendly and helpful")
        else:
            insights.append("they seem neutral and cautious")
        
        # Check target's health
        if target.current_hp < target.max_hp * 0.5:
            insights.append("they look injured or weakened")
        
        # Check for conditions
        if hasattr(target, 'conditions') and target.conditions:
            if 'frightened' in target.conditions:
                insights.append("they are clearly afraid of something")
            if 'charmed' in target.conditions:
                insights.append("their behavior seems unnatural, possibly charmed")
        
        # Check stats for personality insights
        if target.stats.get('cha', 10) >= 14:
            insights.append("they carry themselves with confidence")
        elif target.stats.get('cha', 10) <= 8:
            insights.append("they seem awkward or uncomfortable in social situations")
        
        if target.stats.get('wis', 10) >= 14:
            insights.append("they appear perceptive and alert")
        
        if insights:
            insight_text = ", and ".join(insights)
            print(f"  > {performer.name} senses that {insight_text}.")
        else:
            print(f"  > {performer.name} gets a general read on {target.name} but nothing specific stands out.")