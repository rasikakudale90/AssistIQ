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
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 bg-surface-container-high p-4 rounded border border-outline-variant/30 shadow-xs">
        <div className="flex items-center gap-2">
          <span className="material-symbols-outlined text-primary text-[24px]">menu_book</span>
          <div>
            <span className="font-mono text-[10px] text-primary uppercase font-bold tracking-wider">
              KNOWLEDGE REPOSITORY // RBAC SEARCH
            </span>
            <h1 className="font-headline text-lg font-bold text-on-surface">
              Technical Documentation & Solutions Directory
            </h1>
          </div>
        </div>

        {isStaff && (
          <button
            onClick={() => setCreateModalOpen(true)}
            className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary font-mono text-xs font-bold rounded shadow-xs transition-colors flex items-center gap-1.5 uppercase"
          >
            <span className="material-symbols-outlined text-[16px]">add</span>
            <span>Publish New KB Article</span>
          </button>
        )}
      </div>

      {/* Unified Search Input */}
      <form onSubmit={handleSearch} className="relative">
        <span className="material-symbols-outlined absolute left-3 top-2.5 text-on-surface-variant text-[18px]">
          search
        </span>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Unified full-text search across knowledge articles and permitted support dockets..."
          className="w-full pl-10 pr-24 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface font-mono focus:outline-none focus:ring-1 focus:ring-primary shadow-xs"
        />
        <button
          type="submit"
          className="absolute right-1.5 top-1.5 px-3 py-1 bg-primary hover:bg-primary-container text-on-primary font-mono text-[11px] font-bold rounded"
        >
          Search
        </button>
      </form>

      {/* Unified Search Results View */}
      {loading ? (
        <div className="p-12 text-center font-mono text-xs text-on-surface-variant">
          Loading knowledge repository...
        </div>
      ) : searchResults ? (
        <div className="space-y-4 bg-surface-container-low p-5 rounded border border-outline-variant/30">
          <div className="flex items-center justify-between border-b border-outline-variant/20 pb-2">
            <span className="font-mono text-xs font-bold text-primary uppercase">
              Unified Search Results for "{searchQuery}"
            </span>
            <button
              onClick={() => {
                setSearchResults(null);
                setSearchQuery('');
              }}
              className="text-xs font-mono text-on-surface-variant hover:underline"
            >
              Clear Search
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Articles */}
            <div className="space-y-2">
              <h3 className="font-mono text-xs font-bold text-on-surface uppercase">
                Knowledge Articles ({searchResults.articles.length})
              </h3>
              {searchResults.articles.map((art) => (
                <div
                  key={art.id}
                  onClick={() => {
                    setSelectedArticle(art);
                    setSearchResults(null);
                  }}
                  className="p-3 bg-surface-container-lowest rounded border border-outline-variant/30 hover:border-primary cursor-pointer"
                >
                  <span className="font-mono text-[10px] text-primary block">📁 {art.category}</span>
                  <h4 className="font-headline font-bold text-sm text-on-surface">{art.title}</h4>
                </div>
              ))}
            </div>

            {/* Cases */}
            <div className="space-y-2">
              <h3 className="font-mono text-xs font-bold text-on-surface uppercase">
                Permitted Cases ({searchResults.cases.length})
              </h3>
              {searchResults.cases.map((cs) => (
                <div key={cs.id} className="p-3 bg-surface-container-lowest rounded border border-outline-variant/30">
                  <span className="font-mono text-[10px] text-primary font-bold">#{cs.reference_number}</span>
                  <h4 className="font-headline font-bold text-sm text-on-surface">{cs.title}</h4>
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
          <div className="lg:col-span-4 space-y-2 max-h-[600px] overflow-y-auto">
            {articles.map((art) => (
              <div
                key={art.id}
                onClick={() => setSelectedArticle(art)}
                className={`p-3.5 rounded border transition-all cursor-pointer space-y-1 ${
                  selectedArticle?.id === art.id
                    ? 'bg-surface-container-lowest border-primary shadow-sm ring-1 ring-primary/40'
                    : 'bg-surface-container-lowest border-outline-variant/30 hover:bg-surface-container-low'
                }`}
              >
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-primary font-semibold">📁 {art.category}</span>
                  <span className="text-on-surface-variant text-[10px]">👁 {art.view_count} views</span>
                </div>
                <h3 className="font-headline font-bold text-sm text-on-surface">{art.title}</h3>
              </div>
            ))}
          </div>

          {/* Article Viewer */}
          <div className="lg:col-span-8">
            {selectedArticle ? (
              <div className="bg-surface-container-lowest p-6 rounded-lg border border-outline-variant/30 shadow-xs space-y-4">
                <div className="border-b border-outline-variant/20 pb-3 space-y-1">
                  <div className="flex items-center gap-2 font-mono text-xs text-primary font-semibold">
                    <span>📁 {selectedArticle.category}</span>
                    <span>•</span>
                    <span>Status: {selectedArticle.status}</span>
                  </div>
                  <h2 className="font-headline text-xl font-bold text-on-surface">
                    {selectedArticle.title}
                  </h2>
                </div>

                <div className="font-sans text-sm text-on-surface leading-relaxed whitespace-pre-wrap">
                  {selectedArticle.content}
                </div>
              </div>
            ) : (
              <div className="p-12 text-center bg-surface-container-high rounded-lg border border-outline-variant/30 font-mono text-xs text-on-surface-variant">
                Select a knowledge article to read details.
              </div>
            )}
          </div>
        </div>
      )}

      {/* Create Article Modal */}
      {createModalOpen && (
        <div className="fixed inset-0 z-50 bg-inverse-surface/60 flex items-center justify-center p-4">
          <form onSubmit={handleCreateArticle} className="bg-surface-container-high p-6 rounded-lg max-w-xl w-full space-y-4 border border-outline-variant/40 shadow-xl">
            <h3 className="font-headline font-bold text-lg text-on-surface">
              Publish New Knowledge Base Article
            </h3>
            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1">
                Article Title
              </label>
              <input
                type="text"
                required
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                placeholder="e.g. Modbus Bus Collision Diagnostic Procedure (KB-409)"
                className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface"
              />
            </div>
            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1">
                Category
              </label>
              <select
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                className="w-full px-3 py-2 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface font-mono"
              >
                <option value="Hardware">Hardware</option>
                <option value="Network">Network</option>
                <option value="Software">Software</option>
                <option value="Security">Security</option>
                <option value="Industrial Control">Industrial Control</option>
              </select>
            </div>
            <div>
              <label className="block font-mono text-xs font-semibold text-on-surface-variant uppercase mb-1">
                Markdown / Text Content
              </label>
              <textarea
                required
                rows={8}
                value={content}
                onChange={(e) => setContent(e.target.value)}
                placeholder="Enter procedural instructions, resolution steps, error codes, and troubleshooting workflow..."
                className="w-full p-3 bg-surface-container-lowest border border-outline-variant/40 rounded text-xs text-on-surface font-mono"
              />
            </div>
            <div className="flex justify-end gap-2 pt-2 border-t border-outline-variant/20">
              <button
                type="button"
                onClick={() => setCreateModalOpen(false)}
                className="px-4 py-2 bg-surface-container text-xs font-mono rounded"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={createLoading}
                className="px-4 py-2 bg-primary hover:bg-primary-container text-on-primary text-xs font-mono font-bold rounded shadow-xs uppercase"
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
