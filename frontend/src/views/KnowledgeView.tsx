import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { KnowledgeArticle } from '../api/types';
import { listKnowledgeArticlesApi, createKnowledgeArticleApi, searchUnifiedApi } from '../api/knowledge';

export const KnowledgeView: React.FC = () => {
  const { user } = useAuth();
  const [articles, setArticles] = useState<KnowledgeArticle[]>([]);
  const [selectedArticle, setSelectedArticle] = useState<KnowledgeArticle | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<{ cases: any[]; articles: KnowledgeArticle[] } | null>(null);
  const [loading, setLoading] = useState(true);

  // New Article Modal
  const [createModalOpen, setCreateModalOpen] = useState(false);
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('Hardware');
  const [content, setContent] = useState('');
  const [createLoading, setCreateLoading] = useState(false);

  const isStaff = user && user.role !== 'Requester';

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const data = await listKnowledgeArticlesApi();
      setArticles(data);
      if (data.length > 0 && !selectedArticle) {
        setSelectedArticle(data[0]);
      }
    } catch {
      // Handled
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, []);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      setSearchResults(null);
      return;
    }
    setLoading(true);
    try {
      const results = await searchUnifiedApi(searchQuery);
      setSearchResults(results);
    } catch {
      // Handled
    } finally {
      setLoading(false);
    }
  };

  const handleCreateArticle = async (e: React.FormEvent) => {
    e.preventDefault();
    setCreateLoading(true);
    try {
      const newArt = await createKnowledgeArticleApi({
        title,
        category,
        content,
        status: 'PUBLISHED',
      });
      setCreateModalOpen(false);
      setTitle('');
      setContent('');
      await fetchArticles();
      setSelectedArticle(newArt);
    } catch (err: any) {
      alert(err.response?.data?.message || 'Failed to create article');
    } finally {
      setCreateLoading(false);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 md:px-6 py-6 space-y-6">
      {/* Header Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 liquid-glass p-5 rounded-xl border border-outline-variant/40 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center text-primary shadow-xs">
            <span className="material-symbols-outlined text-[24px]">menu_book</span>
          </div>
          <div>
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-secondary radar-live" />
              <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider">
                KNOWLEDGE REPOSITORY // RBAC SEARCH
              </span>
            </div>
            <h1 className="font-headline text-lg font-bold text-on-surface">
              Technical Documentation & Solutions Directory
            </h1>
          </div>
        </div>

        {isStaff && (
          <button
            onClick={() => setCreateModalOpen(true)}
            className="px-4 py-2.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded-lg shadow-md press-tactile transition-all flex items-center gap-1.5 uppercase tracking-wider"
          >
            <span className="material-symbols-outlined text-[16px]">add</span>
            <span>Publish New KB Article</span>
          </button>
        )}
      </div>

      {/* Unified Search Input */}
      <form onSubmit={handleSearch} className="relative flex items-center">
        <span className="material-symbols-outlined absolute left-3.5 top-1/2 -translate-y-1/2 text-primary dark:text-primary-fixed text-[20px] pointer-events-none z-10 transition-colors">
          search
        </span>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Unified full-text search across knowledge articles and permitted support dockets..."
          className="w-full pl-11 pr-24 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-xl text-xs text-on-surface font-mono input-liquid focus:outline-none shadow-xs"
        />
        <button
          type="submit"
          className="absolute right-2 top-1/2 -translate-y-1/2 px-3.5 py-1.5 bg-primary hover:bg-primary-container text-on-primary font-mono text-[11px] font-bold rounded-lg press-tactile transition-all shadow-xs"
        >
          Search
        </button>
      </form>

      {/* Unified Search Results View */}
      {loading ? (
        <div className="space-y-4 p-4">
          <div className="h-40 liquid-glass rounded-xl shimmer-warm border border-outline-variant/30" />
        </div>
      ) : searchResults ? (
        <div className="space-y-4 liquid-glass-elevated p-5 rounded-xl border border-outline-variant/40 shadow-md">
          <div className="flex items-center justify-between border-b border-outline-variant/20 pb-2.5">
            <span className="font-mono text-xs font-bold text-primary uppercase tracking-wider flex items-center gap-2">
              <span className="material-symbols-outlined text-[16px]">manage_search</span>
              Unified Search Results for "{searchQuery}"
            </span>
            <button
              onClick={() => {
                setSearchResults(null);
                setSearchQuery('');
              }}
              className="text-xs font-mono text-on-surface-variant hover:text-primary press-tactile transition-colors underline"
            >
              Clear Search
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Articles */}
            <div className="space-y-2">
              <h3 className="font-mono text-xs font-bold text-on-surface uppercase tracking-wider">
                Knowledge Articles ({searchResults.articles.length})
              </h3>
              {searchResults.articles.map((art) => (
                <div
                  key={art.id}
                  onClick={() => {
                    setSelectedArticle(art);
                    setSearchResults(null);
                  }}
                  className="p-3.5 liquid-glass-interactive rounded-xl border border-outline-variant/30 cursor-pointer card-3d"
                >
                  <span className="font-mono text-[10px] text-primary block">📁 {art.category}</span>
                  <h4 className="font-headline font-bold text-sm text-on-surface mt-0.5">{art.title}</h4>
                </div>
              ))}
            </div>

            {/* Cases */}
            <div className="space-y-2">
              <h3 className="font-mono text-xs font-bold text-on-surface uppercase tracking-wider">
                Permitted Cases ({searchResults.cases.length})
              </h3>
              {searchResults.cases.map((cs) => (
                <div key={cs.id} className="p-3.5 liquid-glass rounded-xl border border-outline-variant/30">
                  <span className="font-mono text-[10px] text-primary font-bold">#{cs.reference_number}</span>
                  <h4 className="font-headline font-bold text-sm text-on-surface mt-0.5">{cs.title}</h4>
                  <span className="text-[11px] font-mono text-on-surface-variant">Status: {cs.status}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      ) : (
        /* Split Articles Directory */
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Article List */}
          <div className="lg:col-span-4 space-y-2.5 max-h-[600px] overflow-y-auto pr-1">
            {articles.map((art) => (
              <div
                key={art.id}
                onClick={() => setSelectedArticle(art)}
                className={`p-3.5 rounded-xl border transition-all cursor-pointer space-y-1 card-3d ${
                  selectedArticle?.id === art.id
                    ? 'liquid-glass-elevated border-primary shadow-sm ring-1 ring-primary/40'
                    : 'liquid-glass border-outline-variant/30 hover:bg-surface-container/60'
                }`}
              >
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-primary font-bold text-[11px]">📁 {art.category}</span>
                  <span className="text-on-surface-variant text-[10px] bg-surface-container/60 px-2 py-0.5 rounded">👁 {art.view_count} views</span>
                </div>
                <h3 className="font-headline font-bold text-sm text-on-surface">{art.title}</h3>
              </div>
            ))}
          </div>

          {/* Article Viewer */}
          <div className="lg:col-span-8">
            {selectedArticle ? (
              <div className="liquid-glass-elevated p-6 rounded-xl border border-outline-variant/40 shadow-md space-y-4">
                <div className="border-b border-outline-variant/20 pb-3 space-y-1.5">
                  <div className="flex items-center gap-2 font-mono text-xs text-primary font-semibold">
                    <span className="px-2 py-0.5 rounded-md bg-primary/10">📁 {selectedArticle.category}</span>
                    <span>•</span>
                    <span className="text-on-surface-variant">Status: <strong className="text-on-surface">{selectedArticle.status}</strong></span>
                  </div>
                  <h2 className="font-headline text-xl font-bold text-on-surface">
                    {selectedArticle.title}
                  </h2>
                </div>

                <div className="font-sans text-sm text-on-surface leading-relaxed whitespace-pre-wrap pl-3 border-l-2 border-primary/30">
                  {selectedArticle.content}
                </div>
              </div>
            ) : (
              <div className="p-12 text-center liquid-glass rounded-xl border border-outline-variant/30 font-mono text-xs text-on-surface-variant italic">
                Select a knowledge article from the directory to view full contents.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Article Modal */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/40 backdrop-blur-md flex items-center justify-center p-4 animate-fadeIn">
          <form onSubmit={handleCreateArticle} className="liquid-glass-elevated p-6 rounded-xl max-w-xl w-full space-y-4 border border-outline-variant/40 shadow-2xl animate-scaleUp">
            <div className="flex items-center justify-between border-b border-outline-variant/30 pb-3">
              <h3 className="font-headline font-bold text-lg text-on-surface flex items-center gap-2">
                <span className="material-symbols-outlined text-primary text-[20px]">post_add</span>
                Publish New Knowledge Base Article
              </h3>
              <button
                type="button"
                onClick={() => setCreateModalOpen(false)}
                className="w-8 h-8 rounded-lg hover:bg-surface-container/60 flex items-center justify-center text-on-surface-variant press-tactile transition-colors"
              >
                <span className="material-symbols-outlined text-[18px]">close</span>
              </button>
            </div>
            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                Article Title
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Modbus Bus Collision Diagnostic Procedure (KB-409)"
                className="w-full px-3.5 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-lg text-xs text-on-surface input-liquid focus:outline-none"
              />
            </div>
            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-lg text-xs text-on-surface font-mono input-liquid focus:outline-none"
              >
                <option value="Hardware">Hardware</option>
                <option value="Network">Network</option>
                <option value="Software">Software</option>
                <option value="Security">Security</option>
                <option value="Industrial Control">Industrial Control</option>
              </select>
            </div>
            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1.5 tracking-wider">
                Markdown / Text Content
              </label>
              <textarea
                required
                rows={8}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter procedural instructions, resolution steps, error codes, and troubleshooting workflow..."
                className="w-full p-3.5 bg-surface-container-lowest/80 border border-outline-variant/40 rounded-lg text-xs text-on-surface font-mono input-liquid focus:outline-none"
              />
            </div>
            <div className="flex justify-end gap-2.5 pt-3 border-t border-outline-variant/20">
              <button
                type="button"
                onClick={() => setCreateModalOpen(false)}
                className="px-4 py-2 bg-surface-container/60 hover:bg-surface-container text-xs font-mono rounded-lg press-tactile transition-colors"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createLoading}
                className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary text-xs font-mono font-bold rounded-lg shadow-md press-tactile transition-all uppercase tracking-wider disabled:opacity-50"
              >
                {createLoading ? 'Publishing...' : 'Publish Article'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};
