import { apiClient } from './client';
import { KnowledgeArticle } from './types';

export async function listKnowledgeArticlesApi(category?: string, search?: string): Promise<KnowledgeArticle[]> {
  const res = await apiClient.get<any>('/knowledge', {
    params: { category, search },
  });
  const items = Array.isArray(res.data) ? res.data : (res.data?.items || []);
  return items;
}

export async function getKnowledgeArticleApi(id: string): Promise<KnowledgeArticle> {
  const res = await apiClient.get<KnowledgeArticle>(`/knowledge/${id}`);
  return res.data;
}

export async function createKnowledgeArticleApi(payload: {
  title: string;
  category: string;
  content: string;
  status?: 'DRAFT' | 'PUBLISHED' | 'ARCHIVED';
}): Promise<KnowledgeArticle> {
  const res = await apiClient.post<KnowledgeArticle>('/knowledge', payload);
  return res.data;
}

export async function searchUnifiedApi(query: string): Promise<{ cases: any[]; articles: KnowledgeArticle[] }> {
  const res = await apiClient.get<any>('/search', { params: { q: query } });
  const results = res.data?.results || [];
  const cases = results.filter((r: any) => r.type === 'case');
  const articles = results.filter((r: any) => r.type === 'knowledge');
  return { cases, articles };
}
