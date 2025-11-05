import 'package:flutter/material.dart';

class Responsive {
  static double width(BuildContext context) => MediaQuery.of(context).size.width;
  static double height(BuildContext context) => MediaQuery.of(context).size.height;
  
  static bool isMobile(BuildContext context) => width(context) < 600;
  static bool isTablet(BuildContext context) => width(context) >= 600 && width(context) < 1024;
  static bool isDesktop(BuildContext context) => width(context) >= 1024;
  
  // Responsive font sizes
  static double fontSize(BuildContext context, double size) {
    final baseWidth = 375.0; // iPhone 11 Pro width as base
    final currentWidth = width(context);
    return size * (currentWidth / baseWidth);
  }
  
  // Responsive padding
  static double padding(BuildContext context, double size) {
    if (isMobile(context)) return size;
    if (isTablet(context)) return size * 1.5;
    return size * 2;
  }
  
  // Responsive spacing
  static double spacing(BuildContext context, double size) {
    final baseWidth = 375.0;
    final currentWidth = width(context);
    return size * (currentWidth / baseWidth).clamp(0.8, 1.5);
  }
  
  // Safe area padding
  static EdgeInsets safePadding(BuildContext context) {
    return EdgeInsets.only(
      left: padding(context, 16),
      right: padding(context, 16),
      top: MediaQuery.of(context).padding.top + 16,
      bottom: MediaQuery.of(context).padding.bottom + 16,
    );
  }
  
  // Responsive card width
  static double cardWidth(BuildContext context) {
    final w = width(context);
    if (isMobile(context)) return w * 0.9;
    if (isTablet(context)) return 500;
    return 600;
  }
}
