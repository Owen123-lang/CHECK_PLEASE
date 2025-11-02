import { FileText, Plus } from 'lucide-react'; // Ikon

export default function SourcePanel() {
  return (
    <aside className="w-1/5 bg-brand-container p-4 overflow-y-auto border-r border-brand-border hidden md:block">
      <h2 className="text-lg font-bold text-brand-yellow mb-4">Sources</h2>
      <div className="space-y-3">
        <p className="text-gray-500 text-sm">Profile generation sources will appear here.</p>
        
        {/* Placeholder Item 1 */}
        <div className="flex items-center space-x-2 p-3 bg-gray-800 rounded-lg border border-brand-border hover:bg-gray-700 transition-colors cursor-pointer">
          <FileText size={18} className="text-brand-yellow" />
          <p className="font-semibold text-gray-200 truncate">Google Scholar (Placeholder)</p>
        </div>
        {/* Placeholder Item 2 */}
        <div className="flex items-center space-x-2 p-3 bg-gray-800 rounded-lg border border-brand-border hover:bg-gray-700 transition-colors cursor-pointer">
          <FileText size={18} className="text-brand-yellow" />
          <p className="font-semibold text-gray-200 truncate">LinkedIn Profile (Placeholder)</p>
        </div>
      </div>
      <button className="w-full mt-6 flex items-center justify-center space-x-2 bg-brand-yellow text-black font-bold py-2 px-4 rounded-lg hover:bg-brand-yellow-dark transition-colors">
        <Plus size={18} /> <span>Add New Source</span>
      </button>
    </aside>
  );
}
