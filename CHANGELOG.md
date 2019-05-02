## CHANGELOG

### v1.0.0 [20 марта 2019]
- добавлена функция "fetch_items"

### v1.1.0 [10 Апреля 2019]
- добавлена функция "fetch_categories"

### v1.1.1 [23 апреля 2019]
- Updated hooks for fixtures, removed unnecessary fields

### v1.1.2 [23 апреля 2019]
- Syncing for items limited when `In TailPOS` is checked

### v1.1.3 [24 апреля 2019]
- TailPOS app API endpoint updated to get only In TailPOS filtered Items

### v1.1.4 [24 апреля 2019]
- API endpoint for not force sync is updated for In TailPOS filter
- Set Item UUID if not set and that In TailPOS is ticked

### v1.2.0 [24 апреля 2019]
- Clean unnecessary codes
- Added POS Profile field on Tail Settings
- Re-layout Receipts
- Added function, "generated_si"

### v1.2.1 [24 апреля 2019]
- Categories self.id generate, fix for TailPOS category duplicate

### v1.2.2 [25 апреля 2019]
- Added Use Price List field on Tail Settings
- Updated API endpoint for TailOrder to fetch Price List

### v1.2.3 [26 апреля 2019]
- Updated API endpoint for TailPOS to fetch Price List

### v1.3.0 [26 апреля 2019]
- MAJOR: TailPOS will be using name as naming

### v1.3.1 [29 апреля 2019]
- Refactored codes

### v1.3.2 [29 апреля 2019]
- Removed add_role subscriber

### v1.3.3 [29 апреля 2019]
- Added description column from Item for syncing

### v1.3.4 [30 апреля 2019]
- Add Item field on Receipts Item
- Sync Item field in Receipts Item

### v1.3.5 [2 мая 2019]
- fix: barcode field missing on Item

### v1.3.6 [2 мая 2019]
- fix: description to item_name

### v1.4.0 [2 мая 2019]
- fix: total amount on Receipts before_insert
- refactor: sync functions separated create and update
