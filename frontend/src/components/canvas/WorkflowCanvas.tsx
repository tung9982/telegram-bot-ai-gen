import { Background, Controls, MiniMap, ReactFlow, useEdgesState, useNodesState } from '@xyflow/react';
import '@xyflow/react/dist/style.css';
import CustomNode from '../nodes/CustomNode';
import { useWorkflowStore } from '../../stores/workflowStore';
import { useEffect } from 'react';

const nodeTypes = { custom: CustomNode };

export default function WorkflowCanvas() {
  const { nodes, edges, onConnect } = useWorkflowStore();
  const [flowNodes, setFlowNodes, onNodesChange] = useNodesState(nodes);
  const [flowEdges, setFlowEdges, onEdgesChange] = useEdgesState(edges);

  useEffect(() => setFlowNodes(nodes), [nodes, setFlowNodes]);
  useEffect(() => setFlowEdges(edges), [edges, setFlowEdges]);

  return (
    <div className="h-full w-full glass">
      <ReactFlow nodes={flowNodes} edges={flowEdges} onNodesChange={onNodesChange} onEdgesChange={onEdgesChange} onConnect={onConnect} nodeTypes={nodeTypes} fitView>
        <MiniMap />
        <Controls />
        <Background gap={20} color="#334155" />
      </ReactFlow>
    </div>
  );
}
