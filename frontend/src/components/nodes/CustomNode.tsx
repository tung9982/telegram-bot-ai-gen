import { Handle, Position, NodeProps } from '@xyflow/react';
import { motion } from 'framer-motion';

export default function CustomNode({ data }: NodeProps) {
  return (
    <motion.div whileHover={{ scale: 1.03 }} className="glass px-4 py-3 min-w-56 border-cyan-400/40 shadow-cyan-500/20">
      <Handle type="target" position={Position.Left} className="!bg-fuchsia-400" />
      <div className="text-xs uppercase tracking-wide text-cyan-300">{String((data as any).type)}</div>
      <div className="font-semibold text-white">{String((data as any).label)}</div>
      <Handle type="source" position={Position.Right} className="!bg-cyan-400" />
    </motion.div>
  );
}
