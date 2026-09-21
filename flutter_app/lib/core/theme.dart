import 'package:flutter/material.dart';

class AssistIQTheme {
  static const Color primary = Color(0xFF535C32);
  static const Color primaryContainer = Color(0xFF6B7548);
  static const Color onPrimary = Color(0xFFFFFFFF);
  static const Color onPrimaryContainer = Color(0xFFF0FCC4);

  static const Color secondary = Color(0xFFA0401F);
  static const Color secondaryContainer = Color(0xFFFE8760);
  static const Color onSecondary = Color(0xFFFFFFFF);

  static const Color tertiary = Color(0xFF735300);
  static const Color tertiaryContainer = Color(0xFF916A07);

  static const Color surface = Color(0xFFFFF8F2);
  static const Color surfaceContainerLow = Color(0xFFFAF2EA);
  static const Color surfaceContainer = Color(0xFFF4EDE5);
  static const Color surfaceContainerHigh = Color(0xFFEEE7DF);
  static const Color surfaceContainerLowest = Color(0xFFFFFFFF);

  static const Color onSurface = Color(0xFF1E1B17);
  static const Color onSurfaceVariant = Color(0xFF46483D);
  static const Color outline = Color(0xFF77786C);
  static const Color outlineVariant = Color(0xFFC7C7B9);

  static const Color error = Color(0xFFBA1A1A);
  static const Color errorContainer = Color(0xFFFFDAD6);

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: surface,
      colorScheme: const ColorScheme.light(
        primary: primary,
        primaryContainer: primaryContainer,
        onPrimary: onPrimary,
        onPrimaryContainer: onPrimaryContainer,
        secondary: secondary,
        secondaryContainer: secondaryContainer,
        onSecondary: onSecondary,
        tertiary: tertiary,
        tertiaryContainer: tertiaryContainer,
        surface: surface,
        onSurface: onSurface,
        onSurfaceVariant: onSurfaceVariant,
        outline: outline,
        outlineVariant: outlineVariant,
        error: error,
        errorContainer: errorContainer,
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: surfaceContainerLow,
        foregroundColor: onSurface,
        elevation: 0,
        scrolledUnderElevation: 1,
      ),
      cardTheme: CardThemeData(
        color: surfaceContainerLowest,
        elevation: 0,
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: Color(0x4DC7C7B9)),
          borderRadius: BorderRadius.circular(6),
        ),
      ),
    );
  }
}
