"""
Unit tests for Pipeline.
"""
from unittest.mock import Mock
from vibe.core.pipeline import Pipeline, PipelineStage
from vibe.agents.base import AgentResult

def test_pipeline_execution():
    # Setup mock agents
    agent1 = Mock()
    agent1.execute.return_value = AgentResult(
        content="Res1", filename="f1.md", success=True
    )
    agent1.output_filename = "f1.md"
    
    agent2 = Mock()
    agent2.execute.return_value = AgentResult(
        content="Res2", filename="f2.md", success=True
    )
    agent2.output_filename = "f2.md"
    
    stages = [
        PipelineStage(agent=agent1),
        PipelineStage(agent=agent2)
    ]
    
    pipeline = Pipeline(stages)
    initial_context = {"start": "val"}
    
    results = pipeline.run(initial_context)
    
    assert len(results) == 2
    assert results[0].content == "Res1"
    assert results[1].content == "Res2"
    
    # Check context passing
    # agent2.execute should be called with context containing f1 output
    call_args = agent2.execute.call_args[0][0]
    assert call_args["start"] == "val"
    assert call_args["f1"] == "Res1"

def test_pipeline_interactive():
    agent = Mock()
    agent.execute.return_value = AgentResult(
        content="Old", filename="f.md", success=True
    )
    agent.output_filename = "f.md"
    
    stage = PipelineStage(agent=agent, interactive=True)
    pipeline = Pipeline([stage])
    
    def callback(result):
        return "New Content"
        
    results = pipeline.run({}, interactive_callback=callback)
    
    assert results[0].content == "New Content"
