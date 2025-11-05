import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/interaction_provider.dart';
import '../widgets/drug_search_field.dart';
import '../test_data/sample_interaction.dart';
import '../utils/theme.dart';
import 'result_screen.dart';
import 'history_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  String _drugA = '';
  String _drugB = '';
  late AnimationController _animationController;
  late Animation<double> _fadeAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _fadeAnimation = CurvedAnimation(
      parent: _animationController,
      curve: Curves.easeInOut,
    );
    _animationController.forward();
    
    Future.delayed(const Duration(milliseconds: 100), () {
      if (mounted) {
        Provider.of<InteractionProvider>(context, listen: false).checkServerHealth();
      }
    });
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  void _swap() {
    setState(() {
      final temp = _drugA;
      _drugA = _drugB;
      _drugB = temp;
    });
  }

  @override
  Widget build(BuildContext context) {
    final prov = Provider.of<InteractionProvider>(context);

    return Scaffold(
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Color(0xFFF8FAFC),
              Color(0xFFEEF2FF),
            ],
          ),
        ),
        child: SafeArea(
          child: FadeTransition(
            opacity: _fadeAnimation,
            child: SingleChildScrollView(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 20.0, vertical: 16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Header with gradient
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        gradient: const LinearGradient(
                          begin: Alignment.topLeft,
                          end: Alignment.bottomRight,
                          colors: [
                            AppTheme.gradientStart,
                            AppTheme.gradientEnd,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(
                            color: AppTheme.primaryColor.withOpacity(0.3),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: [
                              const Row(
                                children: [
                                  Icon(Icons.medical_services_rounded, color: Colors.white, size: 32),
                                  SizedBox(width: 12),
                                  Text(
                                    'DDI Predictor',
                                    style: TextStyle(
                                      fontSize: 26,
                                      fontWeight: FontWeight.bold,
                                      color: Colors.white,
                                    ),
                                  ),
                                ],
                              ),
                              IconButton(
                                icon: const Icon(Icons.history, color: Colors.white, size: 28),
                                onPressed: () => Navigator.of(context).push(
                                  MaterialPageRoute(builder: (_) => const HistoryScreen()),
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          const Text(
                            'AI-Powered Drug Interaction Screening',
                            style: TextStyle(
                              color: Colors.white70,
                              fontSize: 15,
                            ),
                          ),
                          const SizedBox(height: 16),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                            decoration: BoxDecoration(
                              color: Colors.white.withOpacity(0.2),
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                Icon(
                                  Icons.circle,
                                  size: 10,
                                  color: prov.isServerOnline ? Colors.greenAccent : Colors.redAccent,
                                ),
                                const SizedBox(width: 8),
                                Text(
                                  prov.isServerOnline ? 'Server Online' : 'Server Offline',
                                  style: const TextStyle(
                                    color: Colors.white,
                                    fontSize: 13,
                                    fontWeight: FontWeight.w500,
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),
                    
                    // Stats Cards
                    Row(
                      children: [
                        _buildStatCard(
                          'Total Checks',
                          prov.history.length.toString(),
                          Icons.analytics_outlined,
                          const Color(0xFF6366F1),
                        ),
                        const SizedBox(width: 12),
                        _buildStatCard(
                          'Interactions',
                          prov.history.where((e) => e.interactionExists).length.toString(),
                          Icons.warning_amber_outlined,
                          const Color(0xFFF59E0B),
                        ),
                        const SizedBox(width: 12),
                        _buildStatCard(
                          'Safe',
                          prov.history.where((e) => !e.interactionExists).length.toString(),
                          Icons.check_circle_outline,
                          const Color(0xFF10B981),
                        ),
                      ],
                    ),
                    
                    const SizedBox(height: 28),
                    const Text(
                      'Check Drug Interactions',
                      style: TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1E293B),
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(
                      'Enter two drugs to analyze potential interactions',
                      style: TextStyle(
                        fontSize: 14,
                        color: Colors.grey[600],
                      ),
                    ),
                    const SizedBox(height: 20),
                    
                    // Drug input card with enhanced styling
                    Container(
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(24),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.05),
                            blurRadius: 20,
                            offset: const Offset(0, 10),
                          ),
                        ],
                      ),
                      child: Padding(
                        padding: const EdgeInsets.all(24.0),
                        child: Column(
                          children: [
                            DrugSearchField(
                              label: 'First Drug',
                              initialValue: _drugA,
                              onDrugSelected: (name) => setState(() => _drugA = name),
                            ),
                            const SizedBox(height: 20),
                            // Enhanced swap button
                            Center(
                              child: Container(
                                decoration: BoxDecoration(
                                  gradient: const LinearGradient(
                                    colors: [AppTheme.gradientStart, AppTheme.gradientEnd],
                                  ),
                                  shape: BoxShape.circle,
                                  boxShadow: [
                                    BoxShadow(
                                      color: AppTheme.primaryColor.withOpacity(0.3),
                                      blurRadius: 12,
                                      offset: const Offset(0, 4),
                                    ),
                                  ],
                                ),
                                child: IconButton(
                                  icon: const Icon(Icons.swap_vert_rounded, size: 28, color: Colors.white),
                                  onPressed: _swap,
                                ),
                              ),
                            ),
                            const SizedBox(height: 20),
                            DrugSearchField(
                              label: 'Second Drug',
                              initialValue: _drugB,
                              onDrugSelected: (name) => setState(() => _drugB = name),
                            ),
                            const SizedBox(height: 28),
                            
                            if (prov.error != null)
                              Container(
                                padding: const EdgeInsets.all(16),
                                margin: const EdgeInsets.only(bottom: 20),
                                decoration: BoxDecoration(
                                  color: Colors.red.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(16),
                                  border: Border.all(color: Colors.red.withOpacity(0.3)),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.error_outline, color: Colors.red, size: 24),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Text(
                                        prov.error!,
                                        style: const TextStyle(
                                          color: Colors.red,
                                          fontWeight: FontWeight.w500,
                                        ),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            
                            SizedBox(
                              width: double.infinity,
                              height: 56,
                              child: ElevatedButton(
                                onPressed: prov.isLoading
                                    ? null
                                    : () async {
                                        prov.clearError();
                                        await prov.checkInteraction(_drugA, _drugB);
                                        if (prov.currentResult != null && context.mounted) {
                                          Navigator.of(context).push(
                                            MaterialPageRoute(
                                              builder: (_) => ResultScreen(result: prov.currentResult!),
                                            ),
                                          );
                                        }
                                      },
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppTheme.primaryColor,
                                  foregroundColor: Colors.white,
                                  elevation: 8,
                                  shadowColor: AppTheme.primaryColor.withOpacity(0.4),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(16),
                                  ),
                                ),
                                child: prov.isLoading
                                    ? const SizedBox(
                                        height: 24,
                                        width: 24,
                                        child: CircularProgressIndicator(
                                          color: Colors.white,
                                          strokeWidth: 2.5,
                                        ),
                                      )
                                    : const Row(
                                        mainAxisAlignment: MainAxisAlignment.center,
                                        children: [
                                          Icon(Icons.search, size: 22),
                                          SizedBox(width: 8),
                                          Text(
                                            'Check Interaction',
                                            style: TextStyle(
                                              fontSize: 17,
                                              fontWeight: FontWeight.w600,
                                            ),
                                          ),
                                        ],
                                      ),
                              ),
                            ),
                            const SizedBox(height: 12),
                            SizedBox(
                              width: double.infinity,
                              height: 50,
                              child: OutlinedButton(
                                onPressed: () {
                                  final sample = sampleWarfarinAspirin();
                                  Navigator.push(
                                    context,
                                    MaterialPageRoute(builder: (_) => ResultScreen(result: sample)),
                                  );
                                },
                                style: OutlinedButton.styleFrom(
                                  side: const BorderSide(color: AppTheme.primaryColor, width: 2),
                                  shape: RoundedRectangleBorder(
                                    borderRadius: BorderRadius.circular(16),
                                  ),
                                ),
                                child: const Row(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  children: [
                                    Icon(Icons.preview, size: 20),
                                    SizedBox(width: 8),
                                    Text(
                                      'View Sample Result',
                                      style: TextStyle(
                                        fontSize: 15,
                                        fontWeight: FontWeight.w600,
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                    
                    const SizedBox(height: 24),
                    // Disclaimer
                    Container(
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: Colors.blue.withOpacity(0.08),
                        borderRadius: BorderRadius.circular(16),
                        border: Border.all(color: Colors.blue.withOpacity(0.2)),
                      ),
                      child: Row(
                        children: [
                          Icon(Icons.info_outline, color: Colors.blue[700]),
                          const SizedBox(width: 12),
                          const Expanded(
                            child: Text(
                              'For Healthcare Professionals Only. Not for patient self-diagnosis.',
                              style: TextStyle(fontSize: 13),
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(16),
          boxShadow: [
            BoxShadow(
              color: color.withOpacity(0.1),
              blurRadius: 12,
              offset: const Offset(0, 6),
            ),
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(8),
              ),
              child: Icon(icon, color: color, size: 20),
            ),
            const SizedBox(height: 12),
            Text(
              value,
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              title,
              style: TextStyle(
                fontSize: 12,
                color: Colors.grey[600],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
