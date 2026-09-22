import 'dart:ui';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AssistIQTheme {
  // Brand Olive & Terracotta Palette
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

  // Liquid Glass Decorations (Web-Parity)
  static BoxDecoration liquidGlassDecoration({
    double radius = 16,
    Color? baseColor,
    Border? border,
  }) {
    return BoxDecoration(
      color: baseColor ?? Colors.white.withValues(alpha: 0.82),
      borderRadius: BorderRadius.circular(radius),
      border: border ??
          Border.all(
            color: const Color(0x2E77786C),
            width: 1.0,
          ),
      boxShadow: const [
        BoxShadow(
          color: Color(0x0C1E1B17),
          blurRadius: 20,
          spreadRadius: -2,
          offset: Offset(0, 6),
        ),
      ],
    );
  }

  static BoxDecoration liquidGlassElevatedDecoration({
    double radius = 20,
    Color? baseColor,
  }) {
    return BoxDecoration(
      color: baseColor ?? Colors.white.withValues(alpha: 0.94),
      borderRadius: BorderRadius.circular(radius),
      border: Border.all(
        color: const Color(0x4077786C),
        width: 1.2,
      ),
      boxShadow: const [
        BoxShadow(
          color: Color(0x181E1B17),
          blurRadius: 32,
          spreadRadius: -4,
          offset: Offset(0, 12),
        ),
        BoxShadow(
          color: Color(0x08535C32),
          blurRadius: 12,
          spreadRadius: 0,
          offset: Offset(0, 2),
        ),
      ],
    );
  }

  static InputDecoration liquidInputDecoration({
    required String labelText,
    String? hintText,
    Widget? prefixIcon,
    Widget? suffixIcon,
  }) {
    return InputDecoration(
      labelText: labelText,
      hintText: hintText,
      prefixIcon: prefixIcon,
      suffixIcon: suffixIcon,
      labelStyle: GoogleFonts.inter(
        fontSize: 11,
        fontWeight: FontWeight.w700,
        letterSpacing: 0.5,
        color: onSurfaceVariant,
      ),
      hintStyle: GoogleFonts.inter(
        fontSize: 13,
        color: outline,
      ),
      filled: true,
      fillColor: Colors.white.withValues(alpha: 0.85),
      contentPadding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
      border: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0x3377786C)),
      ),
      enabledBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: Color(0x3377786C)),
      ),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: primary, width: 1.8),
      ),
      errorBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: error),
      ),
    );
  }

  static ThemeData get lightTheme {
    final baseTextTheme = GoogleFonts.interTextTheme();

    return ThemeData(
      useMaterial3: true,
      scaffoldBackgroundColor: surface,
      textTheme: baseTextTheme.copyWith(
        headlineLarge: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: onSurface),
        headlineMedium: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: onSurface),
        headlineSmall: GoogleFonts.outfit(fontWeight: FontWeight.bold, color: onSurface),
        titleLarge: GoogleFonts.outfit(fontWeight: FontWeight.w700, color: onSurface),
        titleMedium: GoogleFonts.inter(fontWeight: FontWeight.w600, color: onSurface),
        bodyLarge: GoogleFonts.inter(color: onSurface),
        bodyMedium: GoogleFonts.inter(color: onSurface),
        labelLarge: GoogleFonts.inter(fontWeight: FontWeight.bold, letterSpacing: 0.5),
      ),
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
      appBarTheme: AppBarTheme(
        backgroundColor: surfaceContainerLowest.withValues(alpha: 0.85),
        foregroundColor: onSurface,
        elevation: 0,
        scrolledUnderElevation: 0.5,
        titleTextStyle: GoogleFonts.outfit(
          fontSize: 16,
          fontWeight: FontWeight.bold,
          color: onSurface,
        ),
      ),
      cardTheme: CardThemeData(
        color: surfaceContainerLowest.withValues(alpha: 0.85),
        elevation: 0,
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: Color(0x33C7C7B9)),
          borderRadius: BorderRadius.circular(12),
        ),
      ),
      elevatedButtonTheme: ElevatedButtonThemeData(
        style: ElevatedButton.styleFrom(
          elevation: 1,
          backgroundColor: primary,
          foregroundColor: Colors.white,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
          padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 12),
          textStyle: GoogleFonts.inter(fontWeight: FontWeight.bold, fontSize: 12, letterSpacing: 0.5),
        ),
      ),
    );
  }
}

class AmbientBackground extends StatelessWidget {
  final Widget child;
  const AmbientBackground({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: const BoxDecoration(
        color: AssistIQTheme.surface,
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color(0xFFFFF8F2),
            Color(0xFFFAF2EA),
            Color(0xFFF4EDE5),
          ],
        ),
      ),
      child: Stack(
        children: [
          Positioned(
            top: -60,
            left: -60,
            child: Container(
              width: 200,
              height: 200,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AssistIQTheme.primaryContainer.withValues(alpha: 0.08),
              ),
            ),
          ),
          Positioned(
            bottom: -80,
            right: -80,
            child: Container(
              width: 240,
              height: 240,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: AssistIQTheme.secondaryContainer.withValues(alpha: 0.08),
              ),
            ),
          ),
          child,
        ],
      ),
    );
  }
}
