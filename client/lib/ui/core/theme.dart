import 'package:flutter/material.dart';

/// Standard Civil Infrastructure Engineering Palette (Institutional TANROADS / AASHTO / Eurocode)
/// Single unified institutional color system with zero decorative gradients.
class CivilColors {
  // Single Primary Brand / Institutional Color
  static const Color primary = Color(0xFF1E3A8A);        // Deep Industrial Navy
  static const Color primaryLight = Color(0xFF2563EB);   // Cobalt Blue (Dark mode primary)
  
  // Neutral Surfaces & Hairline Borders (Solid Matte, Zero Gradients)
  static const Color lightBg = Color(0xFFF8FAFC);        // Slate 50
  static const Color lightSurface = Color(0xFFFFFFFF);   // Pure White
  static const Color lightBorder = Color(0xFFE2E8F0);    // Slate 200
  static const Color lightTextPrimary = Color(0xFF0F172A); // Slate 900
  static const Color lightTextSecondary = Color(0xFF475569); // Slate 600
  static const Color lightTextMuted = Color(0xFF64748B); // Slate 500

  static const Color darkBg = Color(0xFF0B0F19);         // Slate 950
  static const Color darkSurface = Color(0xFF131B2E);    // Slate 900
  static const Color darkBorder = Color(0xFF223049);     // Slate 800
  static const Color darkTextPrimary = Color(0xFFF1F5F9); // Slate 100
  static const Color darkTextSecondary = Color(0xFF94A3B8); // Slate 400
  static const Color darkTextMuted = Color(0xFF64748B); // Slate 500

  // Strictly Functional Condition States (Used only when state triggers, not as decorative trim)
  static const Color healthy = Color(0xFF15803D);        // Muted Forest Green
  static const Color healthyBg = Color(0xFFF0FDF4);
  static const Color healthyDarkBg = Color(0xFF143823);

  static const Color minor = Color(0xFFB45309);          // Muted Amber
  static const Color minorBg = Color(0xFFFFFBEB);
  static const Color minorDarkBg = Color(0xFF38230D);

  static const Color moderate = Color(0xFFC2410C);       // Muted Rust Orange
  static const Color moderateBg = Color(0xFFFFF7ED);
  static const Color moderateDarkBg = Color(0xFF3B1E12);

  static const Color critical = Color(0xFFB91C1C);       // Muted Deep Crimson
  static const Color criticalBg = Color(0xFFFEF2F2);
  static const Color criticalDarkBg = Color(0xFF3C1616);

  // Technical Telemetry Series Colors (Single Primary Accent & Neutral Comparison)
  static const Color seriesPrimary = Color(0xFF2563EB);  // Primary Active Sensor
  static const Color seriesSecondary = Color(0xFF64748B);// Muted Comparison / Drift Baseline
  static const Color seriesThreshold = Color(0xFFDC2626);// Critical Limit Line
  static const Color gridLine = Color(0xFF334155);
  static const Color steelBlue = primary;                // Backward-compatibility alias

  static Color getConditionColor(int conditionIndex) {
    switch (conditionIndex) {
      case 0:
        return healthy;
      case 1:
        return minor;
      case 2:
        return moderate;
      case 3:
      default:
        return critical;
    }
  }

  static Color getConditionBg(int conditionIndex, bool isDark) {
    if (isDark) {
      switch (conditionIndex) {
        case 0:
          return healthyDarkBg;
        case 1:
          return minorDarkBg;
        case 2:
          return moderateDarkBg;
        case 3:
        default:
          return criticalDarkBg;
      }
    } else {
      switch (conditionIndex) {
        case 0:
          return healthyBg;
        case 1:
          return minorBg;
        case 2:
          return moderateBg;
        case 3:
        default:
          return criticalBg;
      }
    }
  }
}

/// Professional Technical System Themes (Zero Gradients, Enterprise Precision)
class CivilEngineeringTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      scaffoldBackgroundColor: CivilColors.darkBg,
      colorScheme: const ColorScheme.dark(
        primary: CivilColors.primaryLight,
        onPrimary: Colors.white,
        secondary: CivilColors.seriesSecondary,
        surface: CivilColors.darkSurface,
        onSurface: CivilColors.darkTextPrimary,
        outline: CivilColors.darkBorder,
      ),
      cardTheme: CardThemeData(
        color: CivilColors.darkSurface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: CivilColors.darkBorder, width: 1),
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: CivilColors.darkSurface,
        elevation: 0,
        scrolledUnderElevation: 0,
        titleTextStyle: TextStyle(
          color: CivilColors.darkTextPrimary,
          fontSize: 14,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.3,
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: CivilColors.darkBorder,
        thickness: 1,
        space: 1,
      ),
      textTheme: const TextTheme(
        titleLarge: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: CivilColors.darkTextPrimary, letterSpacing: -0.2),
        titleMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: CivilColors.darkTextPrimary),
        titleSmall: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: CivilColors.darkTextSecondary, letterSpacing: 0.4),
        bodyLarge: TextStyle(fontSize: 13, color: CivilColors.darkTextPrimary),
        bodyMedium: TextStyle(fontSize: 12, color: CivilColors.darkTextSecondary),
        bodySmall: TextStyle(fontSize: 11, color: CivilColors.darkTextMuted, fontFamily: 'monospace'),
        labelMedium: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: CivilColors.darkTextMuted, letterSpacing: 0.5),
      ),
    );
  }

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      scaffoldBackgroundColor: CivilColors.lightBg,
      colorScheme: const ColorScheme.light(
        primary: CivilColors.primary,
        onPrimary: Colors.white,
        secondary: CivilColors.seriesSecondary,
        surface: CivilColors.lightSurface,
        onSurface: CivilColors.lightTextPrimary,
        outline: CivilColors.lightBorder,
      ),
      cardTheme: CardThemeData(
        color: CivilColors.lightSurface,
        elevation: 0,
        shape: RoundedRectangleBorder(
          side: const BorderSide(color: CivilColors.lightBorder, width: 1),
          borderRadius: BorderRadius.circular(4),
        ),
      ),
      appBarTheme: const AppBarTheme(
        backgroundColor: CivilColors.lightSurface,
        elevation: 0,
        scrolledUnderElevation: 0,
        titleTextStyle: TextStyle(
          color: CivilColors.lightTextPrimary,
          fontSize: 14,
          fontWeight: FontWeight.w600,
          letterSpacing: 0.3,
        ),
      ),
      dividerTheme: const DividerThemeData(
        color: CivilColors.lightBorder,
        thickness: 1,
        space: 1,
      ),
      textTheme: const TextTheme(
        titleLarge: TextStyle(fontSize: 17, fontWeight: FontWeight.w700, color: CivilColors.lightTextPrimary, letterSpacing: -0.2),
        titleMedium: TextStyle(fontSize: 14, fontWeight: FontWeight.w600, color: CivilColors.lightTextPrimary),
        titleSmall: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: CivilColors.lightTextSecondary, letterSpacing: 0.4),
        bodyLarge: TextStyle(fontSize: 13, color: CivilColors.lightTextPrimary),
        bodyMedium: TextStyle(fontSize: 12, color: CivilColors.lightTextSecondary),
        bodySmall: TextStyle(fontSize: 11, color: CivilColors.lightTextMuted, fontFamily: 'monospace'),
        labelMedium: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: CivilColors.lightTextMuted, letterSpacing: 0.5),
      ),
    );
  }
}
