import { create } from 'zustand';
import { Node, Edge, addEdge, Connection } from '@xyflow/react';

type State = { nodes: Node[]; edges: Edge[]; setNodes: (nodes: Node[]) => void; setEdges: (edges: Edge[]) => void; onConnect: (c: Connection) => void; };
export const useWorkflowStore = create<State>((set) => ({
  nodes: [
    { id: 'prompt', type: 'custom', position: { x: 100, y: 100 }, data: { label: 'Prompt Node', type: 'prompt' } },
    { id: 'image', type: 'custom', position: { x: 420, y: 100 }, data: { label: 'Image Generation', type: 'image_generation' } }
  ],
  edges: [{ id: 'e1', source: 'prompt', target: 'image', animated: true }],
  setNodes: (nodes) => set({ nodes }),
  setEdges: (edges) => set({ edges }),
  onConnect: (connection) => set((state) => ({ edges: addEdge({ ...connection, animated: true }, state.edges) })),
}));
