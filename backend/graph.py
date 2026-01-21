from langgraph.graph import START, END, StateGraph
from langgraph.checkpoint.memory import MemorySaver
from backend.planner import (
    PlannerState,
    memory_node,
    timetable_node,
    planner_node,
    workload_reduction_node,
    route_after_review
)
from dotenv import load_dotenv
load_dotenv()

workflow = StateGraph(PlannerState)

workflow.add_node("memory_node", memory_node)
workflow.add_node("timetable_node", timetable_node)
workflow.add_node("planner_node", planner_node)

workflow.add_edge(START, 'memory_node')
workflow.add_edge('memory_node', 'timetable_node')
workflow.add_edge('timetable_node', 'planner_node')
workflow.add_edge('planner_node', END)

checkpointer = MemorySaver()

caesar = workflow.compile(checkpointer=checkpointer, interrupt_before=[])

workflow.add_node('workload_reduction_node',workload_reduction_node)
workflow.add_node('generate_plan', planner_node)

workflow.add_conditional_edges('human_review',route_after_review, {
    'workload_reduction_node': 'generate_plan',
    'replan':'generate_plan',
    'finalize':END
})