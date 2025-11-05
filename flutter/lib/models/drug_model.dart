class DrugModel {
  final String name;
  final String drugClass;

  DrugModel({required this.name, required this.drugClass});

  factory DrugModel.fromJson(Map<String, dynamic> json) {
    return DrugModel(
      name: json['name'] ?? '',
      drugClass: json['drug_class'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'drug_class': drugClass,
    };
  }
}
