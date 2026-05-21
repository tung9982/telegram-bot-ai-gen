import WorkflowCanvas from './components/canvas/WorkflowCanvas';
import './styles/index.css';

export default function App() {
  return (
    <div className="h-screen p-4 grid grid-cols-[280px_1fr_320px] grid-rows-[60px_1fr_220px] gap-3">
      <header className="glass col-span-3 flex items-center px-4 justify-between"><h1 className="font-bold text-xl text-cyan-300">AetherFlow Studio</h1></header>
      <aside className="glass p-4">Node Library</aside>
      <main className="row-span-1"><WorkflowCanvas /></main>
      <aside className="glass p-4">Properties</aside>
      <section className="glass col-span-3 p-4">Runtime Console</section>
    </div>
  );
}
