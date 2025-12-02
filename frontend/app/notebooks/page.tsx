'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, Search, Trash2, Edit2, FileText, Calendar, MoreVertical } from 'lucide-react';
import { useAuth } from '@/contexts/AuthContext';
import ProtectedRoute from '@/components/auth/ProtectedRoute';
import { API_ENDPOINTS } from '@/lib/api';

interface Notebook {
  id: number;
  user_id: number;
  title: string;
  created_at: string;
  updated_at?: string;
}

export default function NotebooksPage() {
  const [notebooks, setNotebooks] = useState<Notebook[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newNotebookTitle, setNewNotebookTitle] = useState('');
  const [isCreating, setIsCreating] = useState(false);
  const [editingNotebook, setEditingNotebook] = useState<Notebook | null>(null);
  const [menuOpenId, setMenuOpenId] = useState<number | null>(null);
  const { logout } = useAuth();

  useEffect(() => {
    fetchNotebooks();
  }, []);

  const getAuthToken = () => {
    return localStorage.getItem('token');
  };

  const fetchNotebooks = async () => {
    try {
      const token = getAuthToken();
      const response = await fetch(API_ENDPOINTS.NOTEBOOKS, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      if (data.success) {
        setNotebooks(data.payload || []);
      }
    } catch (error) {
      console.error('Error fetching notebooks:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateNotebook = async () => {
    if (!newNotebookTitle.trim()) return;

    setIsCreating(true);
    try {
      const token = getAuthToken();
      const response = await fetch(API_ENDPOINTS.NOTEBOOKS, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: newNotebookTitle }),
      });

      const data = await response.json();
      if (data.success) {
        setNotebooks([data.payload, ...notebooks]);
        setShowCreateModal(false);
        setNewNotebookTitle('');
      }
    } catch (error) {
      console.error('Error creating notebook:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleUpdateNotebook = async (id: number, title: string) => {
    if (!title.trim()) {
      alert('Notebook title cannot be empty');
      return;
    }

    // Validate ID before API call
    if (!id || isNaN(id)) {
      console.error('Invalid notebook ID:', id);
      alert('Invalid notebook ID. Please refresh the page.');
      return;
    }

    try {
      const token = getAuthToken();
      const response = await fetch(API_ENDPOINTS.NOTEBOOK(id), {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title: title.trim() }),
      });

      const data = await response.json();
      if (data.success) {
        setNotebooks(notebooks.map(nb => nb.id === id ? data.payload : nb));
        setEditingNotebook(null);
      } else {
        alert('Failed to rename notebook: ' + (data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error updating notebook:', error);
      alert('Error renaming notebook. Please try again.');
    }
  };

  const handleDeleteNotebook = async (id: number) => {
    if (!confirm('Are you sure you want to delete this notebook?')) {
      setMenuOpenId(null);
      return;
    }

    // Validate ID before API call
    if (!id || isNaN(id)) {
      console.error('Invalid notebook ID:', id);
      alert('Invalid notebook ID. Please refresh the page.');
      setMenuOpenId(null);
      return;
    }

    try {
      const token = getAuthToken();
      const response = await fetch(API_ENDPOINTS.NOTEBOOK(id), {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();
      if (data.success) {
        setNotebooks(notebooks.filter(nb => nb.id !== id));
      } else {
        alert('Failed to delete notebook: ' + (data.message || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error deleting notebook:', error);
      alert('Error deleting notebook. Please try again.');
    } finally {
      setMenuOpenId(null);
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  const filteredNotebooks = notebooks.filter(notebook =>
    notebook.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-[#1A1E21] flex flex-col">
      {/* Header */}
      <header className="border-b border-[#2a2a2a] sticky top-0 bg-[#1A1E21]/95 backdrop-blur-sm z-50">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 lg:px-8 py-4 lg:py-6">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3 transition-transform hover:scale-105">
              <img 
                src="/CheckPlease.svg" 
                alt="Check Please" 
                className="h-[35px] sm:h-[40px] lg:h-[55px] w-auto"
              />
            </Link>
            <nav className="flex items-center gap-4 xl:gap-6">
              <Link 
                href="/chat"
                className="text-white text-[16px] xl:text-[20px] font-semibold hover:text-[#FFFF00] transition-all duration-300 relative group"
              >
                Chat
                <span className="absolute bottom-0 left-0 w-0 h-0.5 bg-[#FFFF00] transition-all duration-300 group-hover:w-full" />
              </Link>
              <button
                onClick={logout}
                className="px-6 xl:px-8 py-2 xl:py-3 bg-[#FF0000] text-white text-[16px] xl:text-[20px] font-semibold rounded-[10px] hover:bg-[#D70000] hover:shadow-lg hover:shadow-[#FF0000]/50 transition-all duration-300 transform hover:scale-105"
              >
                Logout
              </button>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
        {/* Top Section */}
        <div className="mb-8">
          <h1 className="text-3xl lg:text-4xl font-bold text-white mb-2">
            Your Notebooks
          </h1>
          <p className="text-base lg:text-lg text-gray-400">
            Create, organize, and manage your research notebooks
          </p>
        </div>

        {/* Search and Create Bar */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="flex-1 relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search notebooks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 bg-[#232B2F] border-2 border-[#2A3339] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#FFFF00] transition-colors"
            />
          </div>
          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center justify-center gap-2 px-6 py-3 bg-[#FF0000] hover:bg-[#D70000] text-white font-semibold rounded-lg transition-all duration-300 hover:shadow-xl"
          >
            <Plus className="w-5 h-5" />
            New Notebook
          </button>
        </div>

        {/* Notebooks Grid */}
        {isLoading ? (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-4 border-[#FFFF00] border-t-transparent rounded-full animate-spin"></div>
            <p className="mt-4 text-gray-400">Loading notebooks...</p>
          </div>
        ) : filteredNotebooks.length === 0 ? (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">
              {searchQuery ? 'No notebooks found' : 'No notebooks yet'}
            </h3>
            <p className="text-gray-400 mb-6">
              {searchQuery ? 'Try adjusting your search' : 'Create your first notebook to get started'}
            </p>
            {!searchQuery && (
              <button
                onClick={() => setShowCreateModal(true)}
                className="inline-flex items-center gap-2 px-6 py-3 bg-[#FF0000] hover:bg-[#D70000] text-white font-semibold rounded-lg transition-all duration-300"
              >
                <Plus className="w-5 h-5" />
                Create Notebook
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredNotebooks.map((notebook) => (
              <div
                key={notebook.id}
                className="bg-[#232B2F] rounded-xl border border-[#2A3339] hover:border-[#FFFF00] transition-all duration-300 hover:shadow-xl group"
              >
                <div className="p-6">
                  <div className="flex items-start justify-between mb-4">
                    <FileText className="w-8 h-8 text-[#FFFF00]" />
                    <div className="relative">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setMenuOpenId(menuOpenId === notebook.id ? null : notebook.id);
                        }}
                        className="p-1 text-gray-400 hover:text-white transition-colors"
                      >
                        <MoreVertical className="w-5 h-5" />
                      </button>
                      {menuOpenId === notebook.id && (
                        <>
                          <div
                            className="fixed inset-0 z-10"
                            onClick={() => setMenuOpenId(null)}
                          />
                          <div className="absolute right-0 mt-2 w-48 bg-[#1A1E21] border border-[#2A3339] rounded-lg shadow-xl z-20">
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                setEditingNotebook(notebook);
                                setMenuOpenId(null);
                              }}
                              className="w-full flex items-center gap-2 px-4 py-3 text-sm text-white hover:bg-[#232B2F] transition-colors rounded-t-lg"
                            >
                              <Edit2 className="w-4 h-4" />
                              Rename
                            </button>
                            <button
                              onClick={(e) => {
                                e.stopPropagation();
                                handleDeleteNotebook(notebook.id);
                              }}
                              className="w-full flex items-center gap-2 px-4 py-3 text-sm text-[#FF0000] hover:bg-[#232B2F] transition-colors rounded-b-lg"
                            >
                              <Trash2 className="w-4 h-4" />
                              Delete
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  </div>
                  <Link href={`/chat?notebook=${notebook.id}`}>
                    <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-[#FFFF00] transition-colors line-clamp-2">
                      {notebook.title}
                    </h3>
                  </Link>
                  <div className="flex items-center gap-2 text-sm text-gray-400">
                    <Calendar className="w-4 h-4" />
                    <span>{formatDate(notebook.created_at)}</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </main>

      {/* Create Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
          <div className="bg-[#232B2F] rounded-2xl border border-[#2A3339] p-6 lg:p-8 w-full max-w-md">
            <h2 className="text-2xl font-bold text-white mb-4">Create New Notebook</h2>
            <input
              type="text"
              placeholder="Notebook title..."
              value={newNotebookTitle}
              onChange={(e) => setNewNotebookTitle(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleCreateNotebook()}
              autoFocus
              className="w-full px-4 py-3 bg-[#1A1E21] border-2 border-[#2A3339] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#FFFF00] transition-colors mb-6"
            />
            <div className="flex gap-3">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setNewNotebookTitle('');
                }}
                className="flex-1 px-4 py-3 bg-[#1A1E21] border border-[#2A3339] text-white rounded-lg hover:bg-[#232B2F] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateNotebook}
                disabled={!newNotebookTitle.trim() || isCreating}
                className="flex-1 px-4 py-3 bg-[#FF0000] hover:bg-[#D70000] text-white font-semibold rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isCreating ? 'Creating...' : 'Create'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Edit Modal */}
      {editingNotebook && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 px-4">
          <div className="bg-[#232B2F] rounded-2xl border border-[#2A3339] p-6 lg:p-8 w-full max-w-md">
            <h2 className="text-2xl font-bold text-white mb-4">Rename Notebook</h2>
            <input
              type="text"
              defaultValue={editingNotebook.title}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleUpdateNotebook(editingNotebook.id, (e.target as HTMLInputElement).value);
                }
              }}
              autoFocus
              className="w-full px-4 py-3 bg-[#1A1E21] border-2 border-[#2A3339] rounded-lg text-white placeholder-gray-500 focus:outline-none focus:border-[#FFFF00] transition-colors mb-6"
              id="edit-title-input"
            />
            <div className="flex gap-3">
              <button
                onClick={() => setEditingNotebook(null)}
                className="flex-1 px-4 py-3 bg-[#1A1E21] border border-[#2A3339] text-white rounded-lg hover:bg-[#232B2F] transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  const input = document.getElementById('edit-title-input') as HTMLInputElement;
                  handleUpdateNotebook(editingNotebook.id, input.value);
                }}
                className="flex-1 px-4 py-3 bg-[#FF0000] hover:bg-[#D70000] text-white font-semibold rounded-lg transition-all"
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
      </div>
    </ProtectedRoute>
  );
}
