import 'package:flutter/material.dart';
import '../utils/constants.dart';

class RiskGauge extends StatelessWidget {
  final double risk; // 0.0 - 1.0
  final String severity;
  final double size;

  const RiskGauge({Key? key, required this.risk, required this.severity, this.size = 200}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final percentage = (risk.clamp(0.0, 1.0) * 100).round();
    final color = AppConstants.getSeverityColor(severity);

    return SizedBox(
      width: size,
      height: size,
      child: TweenAnimationBuilder<double>(
        tween: Tween(begin: 0.0, end: risk),
        duration: const Duration(milliseconds: 1000),
        curve: Curves.easeOutCubic,
        builder: (context, value, child) {
          return Stack(
            alignment: Alignment.center,
            children: [
              SizedBox(
                width: size,
                height: size,
                child: CircularProgressIndicator(
                  value: 1.0,
                  strokeWidth: 14,
                  valueColor: AlwaysStoppedAnimation(Colors.grey.withAlpha((0.2 * 255).round())),
                ),
              ),
              SizedBox(
                width: size,
                height: size,
                child: CircularProgressIndicator(
                  value: value,
                  strokeWidth: 14,
                  valueColor: AlwaysStoppedAnimation(color),
                  backgroundColor: Colors.transparent,
                ),
              ),
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('$percentage%', style: const TextStyle(fontSize: 52, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  Text('${severity.toUpperCase()} RISK', style: TextStyle(color: color, fontWeight: FontWeight.w600)),
                ],
              ),
            ],
          );
        },
      ),
    );
  }
}
