import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../services/api_service.dart';
import '../models/item_model.dart';

final apiServiceProvider = Provider<ApiService>((ref) => ApiService());

final itemsProvider =
    StateNotifierProvider<ItemsNotifier, AsyncValue<List<Item>>>((ref) {
  return ItemsNotifier(ref.read(apiServiceProvider));
});

class ItemsNotifier extends StateNotifier<AsyncValue<List<Item>>> {
  final ApiService _api;

  ItemsNotifier(this._api) : super(const AsyncValue.data([]));

  Future<void> loadLostItems({int page = 1}) async {
    state = const AsyncValue.loading();
    try {
      final response = await _api.getLostItems(page: page);
      final items = (response.data as List)
          .map((json) => Item.fromJson(json, itemType: 'lost'))
          .toList();
      state = AsyncValue.data(items);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }

  Future<void> loadFoundItems({int page = 1}) async {
    state = const AsyncValue.loading();
    try {
      final response = await _api.getFoundItems(page: page);
      final items = (response.data as List)
          .map((json) => Item.fromJson(json, itemType: 'found'))
          .toList();
      state = AsyncValue.data(items);
    } catch (e, st) {
      state = AsyncValue.error(e, st);
    }
  }
}
