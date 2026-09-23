import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
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
    return AmbientBackground(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Search Bar
            Container(
              decoration: AssistIQTheme.liquidGlassDecoration(radius: 12),
              child: TextField(
                controller: _searchCtrl,
                style: GoogleFonts.inter(fontSize: 13, color: AssistIQTheme.onSurface),
                decoration: InputDecoration(
                  hintText: 'Search documentation, procedures, KB articles...',
                  hintStyle: GoogleFonts.inter(fontSize: 13, color: AssistIQTheme.outline),
                  prefixIcon: const Icon(Icons.search, color: AssistIQTheme.primary),
                  suffixIcon: IconButton(
                    icon: const Icon(Icons.arrow_forward, color: AssistIQTheme.primary),
                    onPressed: () => _loadArticles(_searchCtrl.text),
                  ),
                  filled: true,
                  fillColor: Colors.transparent,
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                ),
                onSubmitted: (val) => _loadArticles(val),
              ),
            ),
            const SizedBox(height: 14),

            Expanded(
              child: _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : _articles.isEmpty
                      ? Center(
                          child: Container(
                            padding: const EdgeInsets.all(24),
                            decoration: AssistIQTheme.liquidGlassDecoration(radius: 16),
                            child: Column(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.menu_book, size: 36, color: AssistIQTheme.outline),
                                const SizedBox(height: 10),
                                Text(
                                  'No Knowledge Articles Found',
                                  style: GoogleFonts.outfit(fontSize: 14, fontWeight: FontWeight.bold, color: AssistIQTheme.onSurface),
                                ),
                              ],
                            ),
                          ),
                        )
                      : ListView.separated(
                          itemCount: _articles.length,
                          separatorBuilder: (_, __) => const SizedBox(height: 10),
                          itemBuilder: (context, index) {
                            final art = _articles[index];
                            final isSel = _selectedArticle?['id'] == art['id'];

                            return Container(
                              decoration: AssistIQTheme.liquidGlassDecoration(
                                radius: 14,
                                baseColor: isSel
                                    ? AssistIQTheme.primaryContainer.withValues(alpha: 0.12)
                                    : Colors.white.withValues(alpha: 0.88),
                                border: Border.all(
                                  color: isSel ? AssistIQTheme.primary : const Color(0x3377786C),
                                  width: isSel ? 1.5 : 1.0,
                                ),
                              ),
                              child: ListTile(
                                onTap: () => setState(() => _selectedArticle = art),
                                contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 6),
                                title: Text(
                                  art['title'] ?? '',
                                  style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 13, color: AssistIQTheme.onSurface),
                                ),
                                subtitle: Padding(
                                  padding: const EdgeInsets.only(top: 4),
                                  child: Text(
                                    art['content'] ?? '',
                                    maxLines: 2,
                                    overflow: TextOverflow.ellipsis,
                                    style: GoogleFonts.inter(fontSize: 11, color: AssistIQTheme.onSurfaceVariant, height: 1.3),
                                  ),
                                ),
                                trailing: Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                                  decoration: BoxDecoration(
                                    color: AssistIQTheme.primaryContainer.withValues(alpha: 0.15),
                                    borderRadius: BorderRadius.circular(6),
                                  ),
                                  child: Text(
                                    art['category'] ?? '',
                                    style: GoogleFonts.jetBrainsMono(fontSize: 10, color: AssistIQTheme.primary, fontWeight: FontWeight.bold),
                                  ),
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
