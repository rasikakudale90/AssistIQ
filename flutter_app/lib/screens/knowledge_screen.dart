import 'package:flutter/material.dart';
import '../core/theme.dart';
import '../core/api_client.dart';

class KnowledgeScreen extends StatefulWidget {
  const KnowledgeScreen({super.key});

  @override
  State<KnowledgeScreen> createState() => _KnowledgeScreenState();
}

class _KnowledgeScreenState extends State<KnowledgeScreen> {
  final TextEditingController _searchCtrl = TextEditingController();
  List<dynamic> _articles = [];
  dynamic _selectedArticle;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadArticles();
  }

  Future<void> _loadArticles([String? query]) async {
    setState(() => _isLoading = true);
    try {
      if (query != null && query.trim().isNotEmpty) {
        final res = await ApiClient.get('/search', queryParams: {'q': query.trim()});
        _articles = (res is Map && res['articles'] is List) ? res['articles'] : [];
      } else {
        final res = await ApiClient.get('/knowledge');
        if (res is List) _articles = res;
      }
      if (_articles.isNotEmpty && _selectedArticle == null) {
        _selectedArticle = _articles.first;
      }
    } catch (_) {} finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Search Bar
            TextField(
              controller: _searchCtrl,
              decoration: InputDecoration(
                hintText: 'Search documentation, procedural guides, KB articles...',
                prefixIcon: const Icon(Icons.search),
                suffixIcon: IconButton(
                  icon: const Icon(Icons.arrow_forward),
                  onPressed: () => _loadArticles(_searchCtrl.text),
                ),
                filled: true,
                fillColor: Colors.white,
                border: const OutlineInputBorder(),
                contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
              ),
              onSubmitted: (val) => _loadArticles(val),
            ),
            const SizedBox(height: 12),

            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _articles.isEmpty
                      ? const Center(child: Text('No knowledge articles found.'))
                      : ListView.separated(
                          itemCount: _articles.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 8),
                          itemBuilder: (context, index) {
                            final art = _articles[index];
                            final isSel = _selectedArticle?['id'] == art['id'];

                            return Card(
                              color: isSel ? AssistIQTheme.surfaceContainerHigh : Colors.white,
                              child: ListTile(
                                onTap: () => setState(() => _selectedArticle = art),
                                title: Text(art['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
                                subtitle: Text(
                                  art['content'] ?? '',
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                  style: const TextStyle(fontSize: 11),
                                ),
                                trailing: Text(
                                  art['category'] ?? '',
                                  style: const TextStyle(fontSize: 10, color: AssistIQTheme.primary, fontWeight: FontWeight.bold),
                                ),
                              ),
                            );
                          },
                        ),
            ),
          ],
        ),
      ),
    );
  }
}
