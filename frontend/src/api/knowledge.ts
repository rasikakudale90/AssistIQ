import { apiClient } from './client';
import { KnowledgeArticle } from './types';

export async function listKnowledgeArticlesApi(category?: string): Promise<KnowledgeArticle[]> {
  const res = await apiClient.get<KnowledgeArticle[]>('/knowledge', {
    params: { category },
  });
  return res.data;
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
  const res = await apiClient.get('/search', { params: { q: query } });
  return res.data;
}
