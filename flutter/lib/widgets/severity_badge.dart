import 'package:flutter/material.dart';
import '../utils/constants.dart';

class SeverityBadge extends StatelessWidget {
  final String severity;
  final bool large;

  const SeverityBadge({Key? key, required this.severity, this.large = false}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final color = AppConstants.getSeverityColor(severity);
    final bg = color.withAlpha((0.12 * 255).round());
    final borderColor = color.withAlpha((0.24 * 255).round());
    final text = severity.toUpperCase();
    final icon = _iconForSeverity(severity);

    return Container(
      padding: EdgeInsets.symmetric(horizontal: large ? 16 : 10, vertical: large ? 10 : 6),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: borderColor),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, color: color, size: large ? 20 : 16),
          const SizedBox(width: 8),
          Text('$text SEVERITY', style: TextStyle(color: color, fontWeight: FontWeight.w700, fontSize: large ? 14 : 12)),
        ],
      ),
    );
  }

  IconData _iconForSeverity(String severity) {
    switch (severity.toLowerCase()) {
      case 'low':
        return Icons.check_circle;
      case 'moderate':
        return Icons.warning_amber_rounded;
      case 'high':
        return Icons.error_outline;
      default:
        return Icons.help_outline;
    }
  }
}
