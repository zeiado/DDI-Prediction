import '../models/interaction_result.dart';

InteractionResult sampleWarfarinAspirin() {
  return InteractionResult(
    success: true,
    drugPair: 'Warfarin + Aspirin',
    interactionExists: true,
    severity: 'High',
    riskScore: 8.5,
    description:
        'Concurrent use of warfarin and aspirin significantly increases the risk of major bleeding events. This combination enhances anticoagulant effects through complementary mechanisms, potentially leading to severe hemorrhagic complications including gastrointestinal bleeding, intracranial hemorrhage, and other life-threatening bleeding events.',
    mechanism:
        'Warfarin inhibits vitamin K-dependent synthesis of clotting factors II, VII, IX, and X in the liver, while aspirin irreversibly inhibits cyclooxygenase-1 (COX-1) enzyme, preventing platelet aggregation. This dual anticoagulant and antiplatelet effect creates a synergistic increase in bleeding risk that exceeds the additive effects of either drug alone.',
    recommendations: [
      'Avoid combination unless absolutely necessary for specific high-risk cardiovascular conditions',
      'Monitor INR levels weekly during initial therapy and monthly once stabilized',
      'Educate patient on signs of bleeding: unusual bruising, blood in urine/stool, severe headaches',
      'Consider gastroprotection with proton pump inhibitor (PPI) if combination is unavoidable',
      'Use lowest effective aspirin dose (typically 75-100mg daily) if combination required',
      'Regular assessment of bleeding risk using validated scoring systems (HAS-BLED)',
      'Ensure patient has access to emergency medical care and understands when to seek help'
    ],
    sources: [
      'American Heart Association Guidelines 2023',
      'European Society of Cardiology',
      'Cochrane Database Systematic Review',
      'JAMA Internal Medicine 2022',
      'FDA Drug Safety Communication'
    ],
    timestamp: DateTime.now().toIso8601String(),
  );
}

InteractionResult sampleMetforminIbuprofen() {
  return InteractionResult(
    success: true,
    drugPair: 'Metformin + Ibuprofen',
    interactionExists: true,
    severity: 'Moderate',
    riskScore: 5.5,
    description:
        'NSAIDs like ibuprofen may reduce the glucose-lowering effect of metformin and increase the risk of lactic acidosis, particularly in patients with renal impairment. Additionally, NSAIDs can cause fluid retention and worsen glycemic control.',
    mechanism:
        'Ibuprofen may decrease renal perfusion through prostaglandin inhibition, potentially reducing metformin clearance and increasing plasma levels. This can lead to metformin accumulation and increased risk of lactic acidosis. NSAIDs may also interfere with glucose metabolism and insulin sensitivity.',
    recommendations: [
      'Monitor blood glucose levels more frequently when initiating or discontinuing NSAID therapy',
      'Assess renal function before and during concurrent use',
      'Consider alternative pain management options such as acetaminophen',
      'Use lowest effective NSAID dose for shortest duration necessary',
      'Watch for signs of lactic acidosis: muscle pain, weakness, difficulty breathing, unusual fatigue',
      'Maintain adequate hydration during concurrent therapy'
    ],
    sources: [
      'American Diabetes Association',
      'Clinical Pharmacology & Therapeutics',
      'Diabetes Care Journal 2023'
    ],
    timestamp: DateTime.now().toIso8601String(),
  );
}

InteractionResult sampleLisinoprilPotassium() {
  return InteractionResult(
    success: true,
    drugPair: 'Lisinopril + Potassium Supplements',
    interactionExists: true,
    severity: 'High',
    riskScore: 7.8,
    description:
        'ACE inhibitors like lisinopril combined with potassium supplements can lead to dangerous hyperkalemia (elevated potassium levels), which may cause cardiac arrhythmias and sudden cardiac death.',
    mechanism:
        'Lisinopril reduces aldosterone secretion, which normally promotes potassium excretion by the kidneys. When combined with potassium supplements, this can result in excessive potassium retention, leading to potentially fatal cardiac complications.',
    recommendations: [
      'Avoid routine potassium supplementation in patients taking ACE inhibitors',
      'Monitor serum potassium levels regularly, especially during initiation',
      'Check potassium levels within 1-2 weeks of starting combination',
      'Educate patients to avoid high-potassium foods and salt substitutes',
      'Watch for symptoms: muscle weakness, fatigue, palpitations, irregular heartbeat',
      'Consider alternative blood pressure medications if potassium supplementation is essential'
    ],
    sources: [
      'American College of Cardiology',
      'New England Journal of Medicine',
      'Hypertension Journal 2023'
    ],
    timestamp: DateTime.now().toIso8601String(),
  );
}
