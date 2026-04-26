extends Control

const RESULTS_JSON                 := "res://data/results/latest.json"
const FAVORITES_JSON               := "res://data/user_favorites.json"
const BLACKLIST_JSON               := "res://data/user_blacklist.json"
const PIPELINE_STATE_JSON          := "res://data/results/pipeline_state.json"
const PIPELINE_STOP_FLAG           := "res://data/results/pipeline_stop.flag"
const PIPELINE_SCRIPT              := "res://tools/anfisa_pipeline.py"
const HIDDIFY_IMPORT_HELPER_SCRIPT := "res://tools/hiddify_named_import.py"
const PYTHON_CANDIDATES := [
	"C:/Users/rysla/AppData/Local/Programs/Python/Python38/python.exe",
	"python"
]
const HIDDIFY_EXE    := "C:/Program Files/Hiddify/Hiddify.exe"
const POWERSHELL_EXE := "C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe"

const C_BG      := Color("0a0c17")
const C_SIDE    := Color("0e1122")
const C_CARD    := Color("141628")
const C_ROW     := Color("181b30")
const C_ROW_ALT := Color("1d2038")
const C_BORDER  := Color("252840")
const C_BORDER2 := Color("373a5f")
const C_ACCENT  := Color("8b5cf6")
const C_ACCENT2 := Color("a78bfa")
const C_TXT     := Color("e2e8f0")
const C_DIM     := Color("94a3b8")
const C_MUTED   := Color("64748b")
const C_GREEN   := Color("22c55e")
const C_BLUE    := Color("3b82f6")
const C_ORANGE  := Color("f59e0b")
const C_TEAL    := Color("14b8a6")
const C_RED     := Color("ef4444")
const C_RUN     := Color("7c3aed")

const COUNTRY_FLAGS := {
	"Germany": "🇩🇪", "Netherlands": "🇳🇱", "Poland": "🇵🇱",
	"France": "🇫🇷", "Sweden": "🇸🇪", "Finland": "🇫🇮",
	"Estonia": "🇪🇪", "Russia": "🇷🇺", "Belarus": "🇧🇾",
	"Czechia": "🇨🇿", "Canada": "🇨🇦", "United States": "🇺🇸",
	"United Kingdom": "🇬🇧", "Turkey": "🇹🇷", "Japan": "🇯🇵",
	"Italy": "🇮🇹", "Kazakhstan": "🇰🇿", "Romania": "🇷🇴",
	"Norway": "🇳🇴", "Switzerland": "🇨🇭", "Ukraine": "🇺🇦",
	"Singapore": "🇸🇬", "Brazil": "🇧🇷",
}

const PROTOCOL_COLORS := {
	"trojan": Color("3b82f6"),
	"vless":  Color("8b5cf6"),
	"vmess":  Color("f59e0b"),
	"ss":     Color("14b8a6"),
}

const NAV_KEYS := ["nav_verified", "nav_saved", "nav_blocked", "nav_smarttest", "nav_pipeline"]

const TEXT := {
	"en": {
		"nav_verified": "◈  Verified", "nav_saved": "★  Saved",
		"nav_blocked": "⊘  Blocked", "nav_smarttest": "⚡ Smart Test", "nav_pipeline": "▸  Pipeline",
		"title_verified": "Verified Working Proxies", "title_saved": "Saved Proxies",
		"title_blocked": "Blocked Proxies", "title_pipeline": "Pipeline Output",
		"subtitle_verified": "One entry — one unique exit path",
		"search_hint": "Search by IP, Country...",
		"all_countries": "All Countries", "all_protocols": "All",
		"col_status": "Status", "col_ip": "IP Address", "col_port": "Port",
		"col_country": "Country", "col_isp": "Tag / Region",
		"col_protocol": "Protocol", "col_latency_q": "Quick", "col_latency_r": "Latency",
		"col_score": "Score",
		"working_badge": "● WORKING",
		"fresh_badge": "FRESH", "history_badge": "HISTORY", "seed_badge": "SEED", "unconfirmed_badge": "UNCONF",
		"run_btn": "▶  Run Smart Test", "quick_btn": "⚡  Quick Recovery", "stop_btn": "■  Stop",
		"real_limit": "Real Check Limit",
		"smart_test_title": "Smart Test Control",
		"stage_idle": "Ready to run", "stage_running": "Pipeline running...", "stage_done": "Pipeline finished",
		"live_stats_title": "Live Stats",
		"stat_verified": "Checked", "stat_working": "Fresh", "stat_success": "Visible",
		"source_pool_title": "Source Pool", "snapshot_title": "Last Snapshot",
		"country_focus": "Country Focus", "country_focus_hint": "Netherlands, DE, FR...",
		"exclude_russia": "Exclude Russia",
		"open_hiddify": "Open", "copy": "Copy", "save": "Save",
		"unsave": "Saved ✓", "block": "Block", "unblock": "Unblock",
		"status_copy": "Copied!", "status_opened": "Opened in Hiddify",
		"status_no_hiddify": "Hiddify not found",
		"placeholder_empty": "No verified results yet — run the pipeline first.",
		"placeholder_none": "Nothing working today. Source pool may be weak.",
		"no_run": "No run yet.",
		"footer_made": "Made with love by Ekzar & Anfisa", "all_ok": "All systems purrfect",
		"quote_1": "\"Smart testing.", "quote_2": "Real results. No fluff.\"", "quote_3": "\u2014 Anfisa \ud83d\udc31",
		"runtime": "Runtime",
	},
	"ru": {
		"nav_verified": "◈  Проверенные", "nav_saved": "★  Сохранённые",
		"nav_blocked": "⊘  Чёрный список", "nav_smarttest": "⚡ Умный Тест", "nav_pipeline": "▸  Пайплайн",
		"title_verified": "Подтверждённые Рабочие Прокси", "title_saved": "Сохранённые Прокси",
		"title_blocked": "Заблокированные Прокси", "title_pipeline": "Вывод Пайплайна",
		"subtitle_verified": "Одна запись — один уникальный выход",
		"search_hint": "Поиск по IP, стране...",
		"all_countries": "Все Страны", "all_protocols": "Все",
		"col_status": "Статус", "col_ip": "IP Адрес", "col_port": "Порт",
		"col_country": "Страна", "col_isp": "Тег / Регион",
		"col_protocol": "Протокол", "col_latency_q": "Быстро", "col_latency_r": "Задержка",
		"col_score": "Балл",
		"working_badge": "● РАБОТАЕТ",
		"fresh_badge": "СВЕЖИЕ", "history_badge": "ИСТОРИЯ", "seed_badge": "SEED", "unconfirmed_badge": "UNCONF",
		"run_btn": "▶  Запустить Тест", "quick_btn": "⚡  Быстрое Восстановление", "stop_btn": "■  Стоп",
		"real_limit": "Лимит Проверок",
		"smart_test_title": "Управление Тестом",
		"stage_idle": "Готово к запуску", "stage_running": "Пайплайн запущен...", "stage_done": "Пайплайн завершён",
		"live_stats_title": "Статистика",
		"stat_verified": "Проверено", "stat_working": "Свежие", "stat_success": "Visible",
		"source_pool_title": "Пул Источников", "snapshot_title": "Последний Прогон",
		"country_focus": "Фокус по Странам", "country_focus_hint": "Netherlands, DE, FR...",
		"exclude_russia": "Исключить Россию",
		"open_hiddify": "Hiddify", "copy": "Копия", "save": "Сохр.",
		"unsave": "Сохр. ✓", "block": "ЧС", "unblock": "Убрать",
		"status_copy": "Скопировано!", "status_opened": "Открыто в Hiddify",
		"status_no_hiddify": "Hiddify не найден",
		"placeholder_empty": "Нет проверенных результатов — запустите пайплайн.",
		"placeholder_none": "Сегодня ничего не выжило. Источники слабые.",
		"no_run": "Запусков пока не было.",
		"footer_made": "Сделано с любовью Ekzar & Anfisa", "all_ok": "Все системы мурчат",
		"quote_1": "\"Умное тестирование.", "quote_2": "Реальный результат. Без воды.\"", "quote_3": "\u2014 Anfisa \ud83d\udc31",
		"runtime": "Время",
	}
}

var _pipeline_running := false
var _pipeline_stdout := ""
var _pipeline_pid := -1
var _last_pipeline_state_hash := ""
var _all_results: Array = []
var _fresh_results: Array = []
var _retained_results: Array = []
var _favorite_results: Array = []
var _blocked_results: Array = []
var _stats: Dictionary = {}
var _meta: Dictionary = {}
var _lang := "en"
var _active_nav := 0
var _search_query := ""
var _filter_country := ""
var _filter_protocol := ""
var _pipeline_start_time: int = 0
var _pipeline_mode := "smart"

var _nav_buttons: Array = []
var _main_title_label: Label
var _main_subtitle_label: Label
var _search_input: LineEdit
var _country_filter: OptionButton
var _protocol_filter: OptionButton
var _result_count_label: Label
var _table_body: VBoxContainer
var _log_label: RichTextLabel
var _run_button: Button
var _quick_recovery_button: Button
var _stop_button: Button
var _real_limit_spin: SpinBox
var _country_focus_input: LineEdit
var _exclude_russia_check: CheckBox
var _stage_label: Label
var _progress_bar: ProgressBar
var _stat_verified_label: Label
var _stat_working_label: Label
var _stat_success_label: Label
var _stat_verified_key: Label
var _stat_working_key: Label
var _stat_success_key: Label
var _source_pool_label: RichTextLabel
var _snapshot_label: Label
var _footer_status: Label
var _footer_runtime: Label
var _footer_made: Label
var _lang_en_button: Button
var _lang_ru_button: Button
var _smart_test_title: Label
var _live_stats_title: Label
var _source_pool_title: Label
var _snapshot_title: Label
var _lim_lbl: Label
var _cf_title: Label
var _status_dot: Label
var _status_text_label: Label
var _quote_1: Label
var _quote_2: Label
var _quote_3: Label
var _cat_texture: Texture2D = null
var _cat_frame: PanelContainer
var _nav_indicators: Array = []


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	_load_cat_texture()
	_build_ui()
	_apply_window_settings()
	_sanitize_pipeline_startup_state()
	_load_local_lists()
	_load_latest_results()
	_apply_language()
	_start_status_pulse()
	_start_cat_glow()


func _process(_delta: float) -> void:
	if _pipeline_running:
		_poll_pipeline_state()
	if _pipeline_running and _footer_runtime != null:
		var elapsed := int((Time.get_ticks_msec() - _pipeline_start_time) / 1000)
		_footer_runtime.text = "%s: %02d:%02d" % [_t("runtime"), elapsed / 60, elapsed % 60]


func _notification(what: int) -> void:
	if what == NOTIFICATION_WM_CLOSE_REQUEST and _pipeline_running:
		_on_stop_pressed()


func _sanitize_pipeline_startup_state() -> void:
	var stop_path := ProjectSettings.globalize_path(PIPELINE_STOP_FLAG)
	if FileAccess.file_exists(stop_path):
		DirAccess.remove_absolute(stop_path)
	var state_path := ProjectSettings.globalize_path(PIPELINE_STATE_JSON)
	if not FileAccess.file_exists(state_path):
		_reset_pipeline_ui_idle()
		return
	var parsed = JSON.parse_string(FileAccess.get_file_as_string(state_path))
	if parsed == null or not parsed is Dictionary:
		_reset_pipeline_ui_idle()
		return
	var state: Dictionary = parsed as Dictionary
	var status := str(state.get("status", ""))
	if status == "running":
		state["status"] = "stopped"
		state["stage"] = "idle"
		state["progress"] = 0
		state["message"] = _t("stage_idle")
		var file := FileAccess.open(state_path, FileAccess.WRITE)
		if file != null:
			file.store_string(JSON.stringify(state, "\t"))
	_reset_pipeline_ui_idle()


func _reset_pipeline_ui_idle() -> void:
	_pipeline_running = false
	_pipeline_pid = -1
	_last_pipeline_state_hash = ""
	if _run_button != null:
		_run_button.disabled = false
		_run_button.text = _t("run_btn")
	if _quick_recovery_button != null:
		_quick_recovery_button.disabled = false
		_quick_recovery_button.text = _t("quick_btn")
	if _stop_button != null:
		_stop_button.visible = false
	if _stage_label != null:
		_stage_label.text = _t("stage_idle")
	if _progress_bar != null:
		_progress_bar.value = 0
	if _footer_status != null:
		_footer_status.text = _t("all_ok")
		_footer_status.add_theme_color_override("font_color", C_GREEN)


func _t(k: String) -> String:
	var d: Dictionary = TEXT.get(_lang, TEXT["en"])
	return d.get(k, k)


func _load_cat_texture() -> void:
	var img_path := ProjectSettings.globalize_path("res://assets/anfisa_cat.png")
	if FileAccess.file_exists(img_path):
		var img := Image.new()
		if img.load(img_path) == OK:
			_cat_texture = ImageTexture.create_from_image(img)


func _apply_window_settings() -> void:
	get_window().title = "Anfisa VPN"
	var screen := DisplayServer.screen_get_size()
	var win_w := mini(1720, screen.x - 80)
	var win_h := mini(980, screen.y - 80)
	get_window().size = Vector2i(win_w, win_h)
	get_window().min_size = Vector2i(1440, 860)
	get_window().position = Vector2i((screen.x - win_w) / 2, (screen.y - win_h) / 2)


# =====================================================================
# ANIMATIONS
# =====================================================================

func _start_status_pulse() -> void:
	if _status_dot == null:
		return
	var tw := create_tween().set_loops()
	tw.tween_property(_status_dot, "modulate:a", 0.25, 1.4).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
	tw.tween_property(_status_dot, "modulate:a", 1.0, 1.4).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)


func _start_cat_glow() -> void:
	if _cat_frame == null:
		return
	var tw := create_tween().set_loops()
	tw.tween_property(_cat_frame, "modulate", Color(1.0, 0.95, 1.12, 1.0), 2.5).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)
	tw.tween_property(_cat_frame, "modulate", Color(1.0, 1.0, 1.0, 1.0), 2.5).set_ease(Tween.EASE_IN_OUT).set_trans(Tween.TRANS_SINE)


func _anim_row_enter(panel: Control) -> void:
	var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(panel, "modulate", Color(1.15, 1.15, 1.25, 1.0), 0.12)


func _anim_row_exit(panel: Control) -> void:
	var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(panel, "modulate", Color.WHITE, 0.2)


func _anim_fade_in(node: Control, delay: float) -> void:
	node.modulate.a = 0.0
	var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
	tw.tween_property(node, "modulate:a", 1.0, 0.25).set_delay(delay)


func _anim_btn_press(btn: Button) -> void:
	var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_BACK)
	tw.tween_property(btn, "scale", Vector2(0.94, 0.94), 0.06)
	tw.tween_property(btn, "scale", Vector2.ONE, 0.15)


# =====================================================================
# UI BUILD
# =====================================================================

func _build_ui() -> void:
	var bg := ColorRect.new()
	bg.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	bg.color = C_BG
	add_child(bg)

	var root := HBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.add_theme_constant_override("separation", 0)
	add_child(root)

	root.add_child(_build_sidebar())

	var center := VBoxContainer.new()
	center.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	center.size_flags_vertical = Control.SIZE_EXPAND_FILL
	center.add_theme_constant_override("separation", 0)
	root.add_child(center)

	center.add_child(_build_topbar())

	var split := HSplitContainer.new()
	split.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	split.size_flags_vertical = Control.SIZE_EXPAND_FILL
	split.split_offset = -340
	center.add_child(split)

	split.add_child(_build_main_area())
	split.add_child(_build_right_panel())

	center.add_child(_build_footer())


func _build_sidebar() -> Control:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(260, 0)
	var side_style := StyleBoxFlat.new()
	side_style.bg_color = C_SIDE
	side_style.border_color = C_BORDER
	side_style.border_width_right = 1
	panel.add_theme_stylebox_override("panel", side_style)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 0)
	panel.add_child(vbox)

	var accent_bar := ColorRect.new()
	accent_bar.custom_minimum_size = Vector2(0, 3)
	accent_bar.color = C_ACCENT
	vbox.add_child(accent_bar)

	vbox.add_child(_build_cat_area())

	var sep := HSeparator.new()
	sep.add_theme_color_override("color", C_BORDER)
	vbox.add_child(sep)

	var nav_margin := MarginContainer.new()
	nav_margin.add_theme_constant_override("margin_left", 12)
	nav_margin.add_theme_constant_override("margin_top", 12)
	nav_margin.add_theme_constant_override("margin_right", 12)
	nav_margin.add_theme_constant_override("margin_bottom", 8)
	nav_margin.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_child(nav_margin)

	var nav_vbox := VBoxContainer.new()
	nav_vbox.add_theme_constant_override("separation", 4)
	nav_margin.add_child(nav_vbox)

	_nav_buttons.clear()
	_nav_indicators.clear()
	for i in NAV_KEYS.size():
		var nav_row := HBoxContainer.new()
		nav_row.add_theme_constant_override("separation", 0)
		nav_vbox.add_child(nav_row)
		var indicator := ColorRect.new()
		indicator.custom_minimum_size = Vector2(3, 38)
		indicator.color = C_ACCENT if i == 0 else Color(0, 0, 0, 0)
		nav_row.add_child(indicator)
		_nav_indicators.append(indicator)
		var btn := _make_nav_button(NAV_KEYS[i], i == 0)
		btn.pressed.connect(_on_nav_pressed.bind(i))
		nav_row.add_child(btn)
		_nav_buttons.append(btn)

	var bottom_margin := MarginContainer.new()
	bottom_margin.add_theme_constant_override("margin_left", 14)
	bottom_margin.add_theme_constant_override("margin_right", 14)
	bottom_margin.add_theme_constant_override("margin_bottom", 12)
	vbox.add_child(bottom_margin)

	var status_row := HBoxContainer.new()
	status_row.add_theme_constant_override("separation", 6)
	bottom_margin.add_child(status_row)

	_status_dot = Label.new()
	_status_dot.text = "●"
	_status_dot.add_theme_color_override("font_color", C_GREEN)
	_status_dot.add_theme_font_size_override("font_size", 10)
	status_row.add_child(_status_dot)

	_status_text_label = Label.new()
	_status_text_label.add_theme_font_size_override("font_size", 12)
	_status_text_label.add_theme_color_override("font_color", C_MUTED)
	status_row.add_child(_status_text_label)

	var quote_margin := MarginContainer.new()
	quote_margin.add_theme_constant_override("margin_left", 14)
	quote_margin.add_theme_constant_override("margin_right", 14)
	quote_margin.add_theme_constant_override("margin_bottom", 10)
	vbox.add_child(quote_margin)
	var quote_panel := PanelContainer.new()
	var qs := StyleBoxFlat.new()
	qs.bg_color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.08)
	qs.corner_radius_top_left = 10
	qs.corner_radius_top_right = 10
	qs.corner_radius_bottom_right = 10
	qs.corner_radius_bottom_left = 10
	qs.content_margin_left = 12
	qs.content_margin_top = 10
	qs.content_margin_right = 12
	qs.content_margin_bottom = 10
	quote_panel.add_theme_stylebox_override("panel", qs)
	quote_margin.add_child(quote_panel)
	var quote_vb := VBoxContainer.new()
	quote_vb.add_theme_constant_override("separation", 2)
	quote_panel.add_child(quote_vb)
	_quote_1 = Label.new()
	_quote_1.text = _t("quote_1")
	_quote_1.add_theme_font_size_override("font_size", 12)
	_quote_1.add_theme_color_override("font_color", C_DIM)
	quote_vb.add_child(_quote_1)
	_quote_2 = Label.new()
	_quote_2.text = _t("quote_2")
	_quote_2.add_theme_font_size_override("font_size", 12)
	_quote_2.add_theme_color_override("font_color", C_DIM)
	quote_vb.add_child(_quote_2)
	_quote_3 = Label.new()
	_quote_3.text = _t("quote_3")
	_quote_3.add_theme_font_size_override("font_size", 11)
	_quote_3.add_theme_color_override("font_color", C_ACCENT2)
	_quote_3.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
	quote_vb.add_child(_quote_3)

	return panel


func _build_cat_area() -> Control:
	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 14)
	margin.add_theme_constant_override("margin_top", 18)
	margin.add_theme_constant_override("margin_right", 14)
	margin.add_theme_constant_override("margin_bottom", 12)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 8)
	vbox.alignment = BoxContainer.ALIGNMENT_CENTER
	margin.add_child(vbox)

	var frame_style := StyleBoxFlat.new()
	frame_style.bg_color = Color(0.14, 0.08, 0.30, 1.0)
	frame_style.corner_radius_top_left = 24
	frame_style.corner_radius_top_right = 24
	frame_style.corner_radius_bottom_right = 24
	frame_style.corner_radius_bottom_left = 24
	frame_style.border_color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.3)
	frame_style.border_width_left = 2
	frame_style.border_width_top = 2
	frame_style.border_width_right = 2
	frame_style.border_width_bottom = 2

	_cat_frame = PanelContainer.new()
	_cat_frame.custom_minimum_size = Vector2(190, 190)
	_cat_frame.add_theme_stylebox_override("panel", frame_style)
	_cat_frame.size_flags_horizontal = Control.SIZE_SHRINK_CENTER

	if _cat_texture != null:
		var tex := TextureRect.new()
		tex.texture = _cat_texture
		tex.expand_mode = TextureRect.EXPAND_FIT_WIDTH_PROPORTIONAL
		tex.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		tex.custom_minimum_size = Vector2(186, 186)
		_cat_frame.add_child(tex)
	else:
		var cat_center := CenterContainer.new()
		var cv := VBoxContainer.new()
		cv.alignment = BoxContainer.ALIGNMENT_CENTER
		cv.add_theme_constant_override("separation", -4)
		cat_center.add_child(cv)
		var cat_main := Label.new()
		cat_main.text = "A"
		cat_main.add_theme_font_size_override("font_size", 54)
		cat_main.add_theme_color_override("font_color", C_ACCENT2)
		cat_main.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		cv.add_child(cat_main)
		var cat_sub := Label.new()
		cat_sub.text = "=^..^="
		cat_sub.add_theme_font_size_override("font_size", 14)
		cat_sub.add_theme_color_override("font_color", Color(C_ACCENT2.r, C_ACCENT2.g, C_ACCENT2.b, 0.45))
		cat_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		cv.add_child(cat_sub)
		_cat_frame.add_child(cat_center)

	vbox.add_child(_cat_frame)

	var brand_title := Label.new()
	brand_title.text = "Anfisa VPN"
	brand_title.add_theme_font_size_override("font_size", 26)
	brand_title.add_theme_color_override("font_color", C_TXT)
	brand_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(brand_title)

	var brand_sub := Label.new()
	brand_sub.text = "S M A R T   P R O X Y   L A B"
	brand_sub.add_theme_font_size_override("font_size", 9)
	brand_sub.add_theme_color_override("font_color", C_ACCENT)
	brand_sub.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	vbox.add_child(brand_sub)

	return margin


func _make_nav_button(key: String, active: bool) -> Button:
	var btn := Button.new()
	btn.text = _t(key)
	btn.alignment = HORIZONTAL_ALIGNMENT_LEFT
	btn.custom_minimum_size = Vector2(0, 44)
	btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	btn.add_theme_font_size_override("font_size", 14)
	_style_nav_button(btn, active)
	return btn


func _style_nav_button(btn: Button, active: bool) -> void:
	if active:
		btn.add_theme_color_override("font_color", C_TXT)
		btn.add_theme_stylebox_override("normal", _box(Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.18), C_ACCENT, 10))
		btn.add_theme_stylebox_override("hover",  _box(Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.24), C_ACCENT, 10))
		btn.add_theme_stylebox_override("pressed",_box(Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.30), C_ACCENT, 10))
	else:
		btn.add_theme_color_override("font_color", C_DIM)
		btn.add_theme_stylebox_override("normal", _box(Color(0,0,0,0), Color(0,0,0,0), 10))
		btn.add_theme_stylebox_override("hover",  _box(Color(1,1,1,0.05), Color(0,0,0,0), 10))
		btn.add_theme_stylebox_override("pressed",_box(Color(1,1,1,0.08), Color(0,0,0,0), 10))


func _build_topbar() -> Control:
	var bar := PanelContainer.new()
	bar.custom_minimum_size = Vector2(0, 66)
	var bar_style := StyleBoxFlat.new()
	bar_style.bg_color = C_CARD
	bar_style.border_color = Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.2)
	bar_style.border_width_bottom = 2
	bar.add_theme_stylebox_override("panel", bar_style)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 24)
	margin.add_theme_constant_override("margin_right", 20)
	bar.add_child(margin)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 8)
	margin.add_child(row)

	var title_vbox := VBoxContainer.new()
	title_vbox.add_theme_constant_override("separation", 2)
	title_vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(title_vbox)

	_main_title_label = Label.new()
	_main_title_label.add_theme_font_size_override("font_size", 22)
	_main_title_label.add_theme_color_override("font_color", C_TXT)
	title_vbox.add_child(_main_title_label)

	_main_subtitle_label = Label.new()
	_main_subtitle_label.add_theme_font_size_override("font_size", 12)
	_main_subtitle_label.add_theme_color_override("font_color", C_MUTED)
	title_vbox.add_child(_main_subtitle_label)

	_lang_en_button = _make_lang_btn("EN")
	_lang_en_button.pressed.connect(_set_lang.bind("en"))
	row.add_child(_lang_en_button)

	_lang_ru_button = _make_lang_btn("RU")
	_lang_ru_button.pressed.connect(_set_lang.bind("ru"))
	row.add_child(_lang_ru_button)

	return bar


func _build_main_area() -> Control:
	var vbox := VBoxContainer.new()
	vbox.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.size_flags_vertical = Control.SIZE_EXPAND_FILL
	vbox.add_theme_constant_override("separation", 0)

	vbox.add_child(_build_filter_bar())

	var content := MarginContainer.new()
	content.size_flags_vertical = Control.SIZE_EXPAND_FILL
	content.add_theme_constant_override("margin_left", 18)
	content.add_theme_constant_override("margin_top", 10)
	content.add_theme_constant_override("margin_right", 8)
	content.add_theme_constant_override("margin_bottom", 10)
	vbox.add_child(content)

	var inner := VBoxContainer.new()
	inner.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	inner.size_flags_vertical = Control.SIZE_EXPAND_FILL
	inner.add_theme_constant_override("separation", 4)
	content.add_child(inner)

	inner.add_child(_build_table_header_row())

	var sep := HSeparator.new()
	sep.add_theme_color_override("color", C_BORDER)
	inner.add_child(sep)

	var scroll := ScrollContainer.new()
	scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	inner.add_child(scroll)

	_table_body = VBoxContainer.new()
	_table_body.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_table_body.add_theme_constant_override("separation", 2)
	scroll.add_child(_table_body)

	_log_label = RichTextLabel.new()
	_log_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_log_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_log_label.bbcode_enabled = false
	_log_label.scroll_following = true
	_log_label.add_theme_color_override("default_color", C_DIM)
	_log_label.add_theme_font_size_override("normal_font_size", 13)
	_log_label.visible = false
	inner.add_child(_log_label)

	return vbox


func _build_filter_bar() -> Control:
	var bar := PanelContainer.new()
	bar.custom_minimum_size = Vector2(0, 54)
	var bar_style := StyleBoxFlat.new()
	bar_style.bg_color = Color(C_CARD.r, C_CARD.g, C_CARD.b + 0.02, 1.0)
	bar_style.border_color = C_BORDER
	bar_style.border_width_bottom = 1
	bar.add_theme_stylebox_override("panel", bar_style)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 18)
	margin.add_theme_constant_override("margin_right", 14)
	margin.add_theme_constant_override("margin_top", 4)
	margin.add_theme_constant_override("margin_bottom", 4)
	bar.add_child(margin)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	margin.add_child(row)

	_search_input = LineEdit.new()
	_search_input.custom_minimum_size = Vector2(200, 36)
	_search_input.add_theme_font_size_override("font_size", 13)
	_search_input.add_theme_color_override("font_color", C_TXT)
	_search_input.add_theme_color_override("caret_color", C_ACCENT)
	_search_input.add_theme_stylebox_override("normal", _box(C_BG, C_BORDER, 8))
	_search_input.add_theme_stylebox_override("focus", _box(C_BG, C_ACCENT2, 8))
	_search_input.text_changed.connect(_on_search_changed)
	row.add_child(_search_input)

	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(spacer)

	_country_filter = _make_filter_option(160)
	_country_filter.item_selected.connect(_on_filter_changed)
	row.add_child(_country_filter)

	_protocol_filter = _make_filter_option(100)
	_protocol_filter.item_selected.connect(_on_filter_changed)
	row.add_child(_protocol_filter)

	_result_count_label = Label.new()
	_result_count_label.add_theme_font_size_override("font_size", 13)
	_result_count_label.add_theme_color_override("font_color", C_MUTED)
	row.add_child(_result_count_label)

	return bar


func _make_filter_option(min_w: int) -> OptionButton:
	var opt := OptionButton.new()
	opt.custom_minimum_size = Vector2(min_w, 36)
	opt.add_theme_font_size_override("font_size", 13)
	opt.add_theme_color_override("font_color", C_TXT)
	opt.add_theme_stylebox_override("normal", _box(C_BG, C_BORDER, 8))
	opt.add_theme_stylebox_override("hover",  _box(C_BG, C_BORDER2, 8))
	opt.add_theme_stylebox_override("focus",  _box(C_BG, C_ACCENT2, 8))
	return opt


func _build_table_header_row() -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 0)
	row.custom_minimum_size = Vector2(0, 34)
	var cols := [
		["col_status",   78], ["col_ip",      145], ["col_port",    52],
		["col_country", 128], ["col_isp",     148], ["col_protocol", 74],
		["col_latency_q", 66], ["col_latency_r", 78], ["col_score",  52],
	]
	for col in cols:
		var lbl := Label.new()
		lbl.text = _t(str(col[0]))
		lbl.custom_minimum_size = Vector2(int(col[1]), 0)
		lbl.add_theme_font_size_override("font_size", 11)
		lbl.add_theme_color_override("font_color", Color(C_MUTED.r, C_MUTED.g, C_MUTED.b + 0.05, 1.0))
		lbl.text = lbl.text.to_upper()
		lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		row.add_child(lbl)
	var fill := Control.new()
	fill.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(fill)
	return row


func _build_right_panel() -> Control:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(340, 0)
	var panel_style := StyleBoxFlat.new()
	panel_style.bg_color = C_SIDE
	panel_style.border_color = C_BORDER
	panel_style.border_width_left = 1
	panel.add_theme_stylebox_override("panel", panel_style)

	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	panel.add_child(scroll)

	var outer := MarginContainer.new()
	outer.add_theme_constant_override("margin_left", 14)
	outer.add_theme_constant_override("margin_top", 14)
	outer.add_theme_constant_override("margin_right", 14)
	outer.add_theme_constant_override("margin_bottom", 14)
	scroll.add_child(outer)

	var vbox := VBoxContainer.new()
	vbox.custom_minimum_size = Vector2(308, 0)
	vbox.add_theme_constant_override("separation", 10)
	outer.add_child(vbox)

	vbox.add_child(_build_smart_test_card())
	vbox.add_child(_build_live_stats_card())
	vbox.add_child(_build_source_pool_card())
	vbox.add_child(_build_snapshot_card())
	return panel


func _build_smart_test_card() -> Control:
	var card := _make_card()
	var body := _card_body(card)

	_smart_test_title = Label.new()
	_smart_test_title.add_theme_font_size_override("font_size", 15)
	_smart_test_title.add_theme_color_override("font_color", C_TXT)
	body.add_child(_smart_test_title)

	_stage_label = Label.new()
	_stage_label.add_theme_font_size_override("font_size", 13)
	_stage_label.add_theme_color_override("font_color", C_DIM)
	body.add_child(_stage_label)

	_progress_bar = ProgressBar.new()
	_progress_bar.min_value = 0
	_progress_bar.max_value = 100
	_progress_bar.value = 0
	_progress_bar.show_percentage = false
	_progress_bar.custom_minimum_size = Vector2(0, 6)
	var pb_bg := StyleBoxFlat.new()
	pb_bg.bg_color = C_BORDER
	pb_bg.corner_radius_top_left = 3
	pb_bg.corner_radius_top_right = 3
	pb_bg.corner_radius_bottom_right = 3
	pb_bg.corner_radius_bottom_left = 3
	var pb_fill := StyleBoxFlat.new()
	pb_fill.bg_color = C_ACCENT
	pb_fill.corner_radius_top_left = 3
	pb_fill.corner_radius_top_right = 3
	pb_fill.corner_radius_bottom_right = 3
	pb_fill.corner_radius_bottom_left = 3
	_progress_bar.add_theme_stylebox_override("background", pb_bg)
	_progress_bar.add_theme_stylebox_override("fill", pb_fill)
	body.add_child(_progress_bar)

	_run_button = Button.new()
	_run_button.custom_minimum_size = Vector2(0, 44)
	_run_button.add_theme_font_size_override("font_size", 15)
	_run_button.add_theme_color_override("font_color", Color("ffffff"))
	var run_n := StyleBoxFlat.new()
	run_n.bg_color = C_RUN
	run_n.corner_radius_top_left = 10
	run_n.corner_radius_top_right = 10
	run_n.corner_radius_bottom_right = 10
	run_n.corner_radius_bottom_left = 10
	var run_h := StyleBoxFlat.new()
	run_h.bg_color = C_ACCENT
	run_h.corner_radius_top_left = 10
	run_h.corner_radius_top_right = 10
	run_h.corner_radius_bottom_right = 10
	run_h.corner_radius_bottom_left = 10
	var run_p := StyleBoxFlat.new()
	run_p.bg_color = C_ACCENT2
	run_p.corner_radius_top_left = 10
	run_p.corner_radius_top_right = 10
	run_p.corner_radius_bottom_right = 10
	run_p.corner_radius_bottom_left = 10
	_run_button.add_theme_stylebox_override("normal", run_n)
	_run_button.add_theme_stylebox_override("hover", run_h)
	_run_button.add_theme_stylebox_override("pressed", run_p)
	_run_button.pressed.connect(_on_run_pressed)
	body.add_child(_run_button)

	_quick_recovery_button = Button.new()
	_quick_recovery_button.custom_minimum_size = Vector2(0, 36)
	_quick_recovery_button.add_theme_font_size_override("font_size", 13)
	_quick_recovery_button.add_theme_color_override("font_color", C_TXT)
	_quick_recovery_button.add_theme_stylebox_override("normal", _box(Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.14), C_ACCENT2, 10))
	_quick_recovery_button.add_theme_stylebox_override("hover", _box(Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.26), C_ACCENT2, 10))
	_quick_recovery_button.pressed.connect(_on_quick_recovery_pressed)
	body.add_child(_quick_recovery_button)

	_stop_button = Button.new()
	_stop_button.custom_minimum_size = Vector2(0, 36)
	_stop_button.visible = false
	_stop_button.add_theme_font_size_override("font_size", 13)
	_stop_button.add_theme_color_override("font_color", C_TXT)
	_stop_button.add_theme_stylebox_override("normal", _box(C_BORDER, C_BORDER2, 10))
	_stop_button.add_theme_stylebox_override("hover", _box(C_BORDER2, C_BORDER2, 10))
	_stop_button.pressed.connect(_on_stop_pressed)
	body.add_child(_stop_button)

	var sep := HSeparator.new()
	sep.add_theme_color_override("color", C_BORDER)
	body.add_child(sep)

	_cf_title = Label.new()
	_cf_title.add_theme_font_size_override("font_size", 12)
	_cf_title.add_theme_color_override("font_color", C_MUTED)
	body.add_child(_cf_title)

	_country_focus_input = LineEdit.new()
	_country_focus_input.custom_minimum_size = Vector2(0, 34)
	_country_focus_input.add_theme_font_size_override("font_size", 13)
	_country_focus_input.add_theme_color_override("font_color", C_TXT)
	_country_focus_input.add_theme_stylebox_override("normal", _box(C_BG, C_BORDER, 8))
	_country_focus_input.add_theme_stylebox_override("focus", _box(C_BG, C_ACCENT2, 8))
	body.add_child(_country_focus_input)

	_exclude_russia_check = CheckBox.new()
	_exclude_russia_check.add_theme_font_size_override("font_size", 13)
	_exclude_russia_check.add_theme_color_override("font_color", C_DIM)
	_exclude_russia_check.button_pressed = false
	body.add_child(_exclude_russia_check)

	var lim_row := HBoxContainer.new()
	lim_row.add_theme_constant_override("separation", 8)
	body.add_child(lim_row)

	_lim_lbl = Label.new()
	_lim_lbl.add_theme_font_size_override("font_size", 12)
	_lim_lbl.add_theme_color_override("font_color", C_MUTED)
	_lim_lbl.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	lim_row.add_child(_lim_lbl)

	_real_limit_spin = SpinBox.new()
	_real_limit_spin.min_value = 8
	_real_limit_spin.max_value = 80
	_real_limit_spin.step = 2
	_real_limit_spin.value = 28
	_real_limit_spin.custom_minimum_size = Vector2(90, 34)
	lim_row.add_child(_real_limit_spin)

	return card


func _build_live_stats_card() -> Control:
	var card := _make_card()
	var body := _card_body(card)

	_live_stats_title = Label.new()
	_live_stats_title.add_theme_font_size_override("font_size", 14)
	_live_stats_title.add_theme_color_override("font_color", C_TXT)
	body.add_child(_live_stats_title)
	var stats_sep := HSeparator.new()
	stats_sep.add_theme_color_override("color", Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.15))
	body.add_child(stats_sep)

	var grid := GridContainer.new()
	grid.columns = 3
	grid.add_theme_constant_override("h_separation", 10)
	grid.add_theme_constant_override("v_separation", 4)
	body.add_child(grid)

	var vb: Array = _add_stat_block("—", grid)
	_stat_verified_label = vb[0] as Label
	_stat_verified_key = vb[1] as Label

	var wb: Array = _add_stat_block("—", grid)
	_stat_working_label = wb[0] as Label
	_stat_working_key = wb[1] as Label

	var sb: Array = _add_stat_block("—%", grid)
	_stat_success_label = sb[0] as Label
	_stat_success_key = sb[1] as Label

	return card


func _add_stat_block(initial: String, parent: Control) -> Array:
	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 2)
	parent.add_child(vbox)
	var val := Label.new()
	val.text = initial
	val.add_theme_font_size_override("font_size", 26)
	val.add_theme_color_override("font_color", C_ACCENT2)
	vbox.add_child(val)
	var key_lbl := Label.new()
	key_lbl.add_theme_font_size_override("font_size", 11)
	key_lbl.add_theme_color_override("font_color", C_MUTED)
	vbox.add_child(key_lbl)
	return [val, key_lbl]


func _build_source_pool_card() -> Control:
	var card := _make_card()
	var body := _card_body(card)

	_source_pool_title = Label.new()
	_source_pool_title.add_theme_font_size_override("font_size", 14)
	_source_pool_title.add_theme_color_override("font_color", C_TXT)
	body.add_child(_source_pool_title)
	var pool_sep := HSeparator.new()
	pool_sep.add_theme_color_override("color", Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.15))
	body.add_child(pool_sep)

	_source_pool_label = RichTextLabel.new()
	_source_pool_label.bbcode_enabled = true
	_source_pool_label.fit_content = true
	_source_pool_label.custom_minimum_size = Vector2(0, 60)
	_source_pool_label.add_theme_font_size_override("normal_font_size", 13)
	_source_pool_label.add_theme_color_override("default_color", C_DIM)
	body.add_child(_source_pool_label)

	return card


func _build_snapshot_card() -> Control:
	var card := _make_card()
	var body := _card_body(card)

	_snapshot_title = Label.new()
	_snapshot_title.add_theme_font_size_override("font_size", 14)
	_snapshot_title.add_theme_color_override("font_color", C_TXT)
	body.add_child(_snapshot_title)
	var snap_sep := HSeparator.new()
	snap_sep.add_theme_color_override("color", Color(C_ACCENT.r, C_ACCENT.g, C_ACCENT.b, 0.15))
	body.add_child(snap_sep)

	_snapshot_label = Label.new()
	_snapshot_label.add_theme_font_size_override("font_size", 12)
	_snapshot_label.add_theme_color_override("font_color", C_MUTED)
	_snapshot_label.text = "—"
	body.add_child(_snapshot_label)

	return card


func _build_footer() -> Control:
	var bar := PanelContainer.new()
	bar.custom_minimum_size = Vector2(0, 34)
	var bar_style := StyleBoxFlat.new()
	bar_style.bg_color = C_SIDE
	bar_style.border_color = C_BORDER
	bar_style.border_width_top = 1
	bar.add_theme_stylebox_override("panel", bar_style)

	var margin := MarginContainer.new()
	margin.add_theme_constant_override("margin_left", 14)
	margin.add_theme_constant_override("margin_right", 14)
	bar.add_child(margin)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 18)
	margin.add_child(row)

	_footer_made = Label.new()
	_footer_made.text = "v2.0.0  🐾  " + _t("footer_made")
	_footer_made.add_theme_font_size_override("font_size", 12)
	_footer_made.add_theme_color_override("font_color", C_MUTED)
	row.add_child(_footer_made)

	var spacer := Control.new()
	spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(spacer)

	_footer_status = Label.new()
	_footer_status.add_theme_font_size_override("font_size", 12)
	_footer_status.add_theme_color_override("font_color", C_GREEN)
	row.add_child(_footer_status)

	_footer_runtime = Label.new()
	_footer_runtime.add_theme_font_size_override("font_size", 12)
	_footer_runtime.add_theme_color_override("font_color", C_MUTED)
	row.add_child(_footer_runtime)

	return bar


# =====================================================================
# STYLE HELPERS
# =====================================================================

func _box(bg: Color, border: Color = Color(0, 0, 0, 0), r: int = 0) -> StyleBoxFlat:
	var s := StyleBoxFlat.new()
	s.bg_color = bg
	s.border_color = border
	var bw: int = 1 if border.a > 0.01 else 0
	s.border_width_left = bw
	s.border_width_top = bw
	s.border_width_right = bw
	s.border_width_bottom = bw
	s.corner_radius_top_left = r
	s.corner_radius_top_right = r
	s.corner_radius_bottom_right = r
	s.corner_radius_bottom_left = r
	s.content_margin_left = 8
	s.content_margin_top = 6
	s.content_margin_right = 8
	s.content_margin_bottom = 6
	return s


func _make_card() -> PanelContainer:
	var p := PanelContainer.new()
	var cs := StyleBoxFlat.new()
	cs.bg_color = C_CARD
	cs.border_color = C_BORDER
	cs.border_width_left = 1
	cs.border_width_right = 1
	cs.border_width_bottom = 1
	cs.border_width_top = 2
	cs.corner_radius_top_left = 12
	cs.corner_radius_top_right = 12
	cs.corner_radius_bottom_right = 12
	cs.corner_radius_bottom_left = 12
	p.add_theme_stylebox_override("panel", cs)
	return p


func _card_body(card: PanelContainer) -> VBoxContainer:
	var m := MarginContainer.new()
	m.add_theme_constant_override("margin_left", 16)
	m.add_theme_constant_override("margin_top", 14)
	m.add_theme_constant_override("margin_right", 16)
	m.add_theme_constant_override("margin_bottom", 14)
	card.add_child(m)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 10)
	m.add_child(v)
	return v


func _make_lang_btn(text: String) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(40, 32)
	btn.add_theme_font_size_override("font_size", 13)
	btn.add_theme_color_override("font_color", C_TXT)
	btn.add_theme_stylebox_override("normal", _box(C_BORDER, Color(0,0,0,0), 8))
	btn.add_theme_stylebox_override("hover", _box(C_BORDER2, Color(0,0,0,0), 8))
	btn.add_theme_stylebox_override("pressed", _box(C_ACCENT, Color(0,0,0,0), 8))
	return btn


# =====================================================================
# LANGUAGE / NAV
# =====================================================================

func _apply_language() -> void:
	_search_input.placeholder_text = _t("search_hint")
	_smart_test_title.text = _t("smart_test_title")
	_live_stats_title.text = _t("live_stats_title")
	_source_pool_title.text = _t("source_pool_title")
	_snapshot_title.text = _t("snapshot_title")
	_stage_label.text = _t("stage_idle") if not _pipeline_running else _t("stage_running")
	_run_button.text = _t("run_btn")
	if _quick_recovery_button != null:
		_quick_recovery_button.text = _t("quick_btn")
	_stop_button.text = _t("stop_btn")
	_lim_lbl.text = _t("real_limit")
	_cf_title.text = _t("country_focus")
	_country_focus_input.placeholder_text = _t("country_focus_hint")
	_exclude_russia_check.text = _t("exclude_russia")
	_status_text_label.text = _t("all_ok")
	_footer_status.text = _t("all_ok")
	_footer_made.text = "v2.0.0  🐾  " + _t("footer_made")
	_quote_1.text = _t("quote_1")
	_quote_2.text = _t("quote_2")
	_quote_3.text = _t("quote_3")
	if _stat_verified_key != null:
		_stat_verified_key.text = _t("stat_verified")
	if _stat_working_key != null:
		_stat_working_key.text = _t("stat_working")
	if _stat_success_key != null:
		_stat_success_key.text = _t("stat_success")
	_update_nav_texts()
	_update_title_for_nav()
	_rebuild_country_filter()
	_rebuild_protocol_filter()
	_style_lang_buttons()
	_rebuild_table()


func _style_lang_buttons() -> void:
	var active_s := _box(C_ACCENT, Color(0, 0, 0, 0), 8)
	var idle_s   := _box(C_BORDER, Color(0, 0, 0, 0), 8)
	_lang_en_button.add_theme_stylebox_override("normal", active_s if _lang == "en" else idle_s)
	_lang_ru_button.add_theme_stylebox_override("normal", active_s if _lang == "ru" else idle_s)
	_lang_en_button.add_theme_color_override("font_color", C_TXT if _lang == "en" else C_DIM)
	_lang_ru_button.add_theme_color_override("font_color", C_TXT if _lang == "ru" else C_DIM)


func _set_lang(lang: String) -> void:
	_lang = lang
	_apply_language()


func _update_nav_texts() -> void:
	for i in _nav_buttons.size():
		_nav_buttons[i].text = _t(NAV_KEYS[i])


func _update_title_for_nav() -> void:
	var title_map := {
		"nav_verified": "title_verified", "nav_saved": "title_saved",
		"nav_blocked": "title_blocked", "nav_smarttest": "title_verified",
		"nav_pipeline": "title_pipeline"
	}
	var key: String = NAV_KEYS[_active_nav] if _active_nav < NAV_KEYS.size() else NAV_KEYS[0]
	_main_title_label.text = _t(title_map.get(key, "title_verified"))
	_main_subtitle_label.text = _t("subtitle_verified") if _active_nav == 0 else ""


func _on_nav_pressed(index: int) -> void:
	_active_nav = index
	for i in _nav_buttons.size():
		_style_nav_button(_nav_buttons[i], i == index)
		if i < _nav_indicators.size():
			var tw := create_tween().set_ease(Tween.EASE_OUT).set_trans(Tween.TRANS_CUBIC)
			tw.tween_property(_nav_indicators[i], "color", C_ACCENT if i == index else Color(0,0,0,0), 0.2)
	_update_title_for_nav()
	var show_log := (index == 4)
	_table_body.visible = not show_log
	_log_label.visible = show_log
	if show_log:
		_log_label.text = _pipeline_stdout if _pipeline_stdout != "" else _t("no_run")
	_rebuild_table()


# =====================================================================
# DATA LOADING
# =====================================================================

func _load_latest_results() -> void:
	var path := ProjectSettings.globalize_path(RESULTS_JSON)
	if not FileAccess.file_exists(path):
		_all_results = []
		_fresh_results = []
		_retained_results = []
		_rebuild_table()
		return
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		_all_results = []
		_fresh_results = []
		_retained_results = []
		_rebuild_table()
		return
	var parsed = JSON.parse_string(file.get_as_text())
	file.close()
	if parsed == null or not parsed is Dictionary:
		_all_results = []
		_fresh_results = []
		_retained_results = []
		_rebuild_table()
		return
	var pd: Dictionary = parsed as Dictionary
	_fresh_results = pd.get("fresh_results", [])
	_retained_results = pd.get("retained_results", [])
	_all_results = pd.get("recommended_results", pd.get("displayed_results", pd.get("working", [])))
	_meta  = pd.get("meta", {})
	_stats = pd.get("stats", {})
	_rebuild_country_filter()
	_rebuild_protocol_filter()
	_refresh_stats()
	_rebuild_table()


func _refresh_stats() -> void:
	var total   := int(_stats.get("checked_total", _stats.get("real_checked", _stats.get("parsed_candidates", 0))))
	var fresh := int(_stats.get("fresh_live_total", _stats.get("fresh_recommended_total", _fresh_results.size())))
	var retained := int(_stats.get("retained_total", _retained_results.size()))
	var seed_confirmed := int(_stats.get("seed_confirmed_total", 0))
	var history_total := int(_stats.get("history_total", retained))
	var unconfirmed_total := int(_stats.get("unconfirmed_seed_total", 0))
	var visible := int(_stats.get("recommended_visible_total", _stats.get("visible_total", _all_results.size())))
	var runtime_seconds := int(_stats.get("runtime_seconds", 0))
	_stat_verified_label.text = str(total)
	_stat_working_label.text  = str(fresh)
	_stat_success_label.text  = str(visible)
	var parsed_counts = _stats.get("parsed_candidates", null)
	if parsed_counts is Dictionary:
		var lines := PackedStringArray()
		for proto in parsed_counts:
			lines.append("[b]%s[/b]: %s" % [proto.to_upper(), str(int(parsed_counts[proto]))])
		_source_pool_label.text = "\n".join(lines)
	else:
		_source_pool_label.text = "—"
	var ts := str(_meta.get("started_at", "—"))
	var slow_count := int(_stats.get("slow_hidden_total", _stats.get("fresh_slow_total", 0)))
	_snapshot_label.text = "Run: %s\nFresh: %d\nSeed: %d\nHistory: %d\nUnconfirmed: %d\nVisible: %d\nRuntime: %ds\nSlow hidden: %d" % [ts, fresh, seed_confirmed, history_total, unconfirmed_total, visible, runtime_seconds, slow_count]


# =====================================================================
# TABLE
# =====================================================================

func _rebuild_table() -> void:
	for child in _table_body.get_children():
		child.queue_free()
	if _active_nav == 4:
		return
	var source := _get_display_source()
	var filtered := _get_filtered_results(source)
	_result_count_label.text = str(filtered.size())
	if filtered.is_empty():
		var ph := Label.new()
		ph.text = _t("placeholder_empty") if _all_results.is_empty() else _t("placeholder_none")
		ph.add_theme_color_override("font_color", C_MUTED)
		ph.add_theme_font_size_override("font_size", 14)
		ph.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		_table_body.add_child(ph)
		return
	for i in filtered.size():
		var row_panel := _make_result_row(filtered[i], i)
		_table_body.add_child(row_panel)
		_anim_fade_in(row_panel, float(i) * 0.04)


func _get_display_source() -> Array:
	match _active_nav:
		1: return _favorite_results
		2: return _blocked_results
		_: return _all_results


func _get_filtered_results(source: Array) -> Array:
	var out: Array = []
	for r in source:
		var config := str(r.get("config", ""))
		if _active_nav != 2 and _has_config(_blocked_results, config):
			continue
		if _active_nav == 0 and not bool(r.get("recommended", false)):
			continue
		if _filter_country != "":
			var country := str(r.get("exit_country", r.get("region", ""))).to_lower()
			if country != _filter_country.to_lower():
				continue
		if _filter_protocol != "":
			var proto := str(r.get("protocol", "")).to_lower()
			if proto != _filter_protocol.to_lower():
				continue
		if _search_query != "":
			var q := _search_query.to_lower()
			var haystack := (str(r.get("endpoint", "")) + " " + str(r.get("exit_ip", "")) + " " +
				str(r.get("exit_country", r.get("region", ""))) + " " + str(r.get("tag", ""))).to_lower()
			if not haystack.contains(q):
				continue
		out.append(r)
	return out


func _make_result_row(result: Dictionary, index: int) -> Control:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(0, 54)
	panel.mouse_filter = Control.MOUSE_FILTER_STOP
	panel.mouse_entered.connect(_anim_row_enter.bind(panel))
	panel.mouse_exited.connect(_anim_row_exit.bind(panel))
	var rs := StyleBoxFlat.new()
	rs.bg_color = C_ROW if index % 2 == 0 else C_ROW_ALT
	rs.corner_radius_top_left = 8
	rs.corner_radius_top_right = 8
	rs.corner_radius_bottom_right = 8
	rs.corner_radius_bottom_left = 8
	var proto_key  := str(result.get("protocol", "")).to_lower()
	var proto_clr: Color = PROTOCOL_COLORS.get(proto_key, C_MUTED)
	rs.border_color = proto_clr
	rs.border_width_left = 3
	rs.content_margin_left = 10
	rs.content_margin_top = 4
	rs.content_margin_right = 6
	rs.content_margin_bottom = 4
	panel.add_theme_stylebox_override("panel", rs)

	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 0)
	panel.add_child(row)

	var protocol   := proto_key
	var endpoint   := str(result.get("endpoint", ""))
	var exit_country := str(result.get("exit_country", result.get("region", "Unknown")))
	var quick_ms   = result.get("quick_latency_ms", null)
	var real_ms    = result.get("real_latency_ms", null)
	var score      = result.get("score", null)
	var tag        := str(result.get("tag", ""))
	var source_kind := str(result.get("source_kind", "fresh"))
	var verification_tier_default := "live_confirmed"
	if source_kind != "fresh":
		verification_tier_default = "history_retained"
	var verification_tier := str(result.get("verification_tier", verification_tier_default))
	var quality_tier := str(result.get("quality_tier", "unknown"))

	var host := ""
	var port_str := ""
	var colon_pos := endpoint.rfind(":")
	if colon_pos >= 0:
		host = endpoint.substr(0, colon_pos)
		port_str = endpoint.substr(colon_pos + 1)
	else:
		host = endpoint

	_row_cell(row, _make_working_badge(source_kind, verification_tier, quality_tier), 124)
	_row_cell(row, _make_lbl(host, C_TXT, 13), 145)
	_row_cell(row, _make_lbl(port_str, C_DIM, 13), 52)
	_row_cell(row, _make_lbl(_get_flag(exit_country) + " " + exit_country, C_TXT, 13), 128)
	_row_cell(row, _make_lbl(tag.substr(0, 16) if tag.length() > 16 else tag, C_DIM, 12), 148)
	_row_cell(row, _make_protocol_badge(protocol), 74)
	var qc := C_GREEN if quick_ms != null and quick_ms <= 180 else C_BLUE if quick_ms != null and quick_ms <= 300 else C_ORANGE if quick_ms != null and quick_ms <= 700 else C_RED
	var rc := C_GREEN if real_ms  != null and real_ms  <= 180 else C_BLUE if real_ms  != null and real_ms  <= 300 else C_ORANGE if real_ms  != null and real_ms  <= 700 else C_RED
	_row_cell(row, _make_lbl(("%d ms" % int(quick_ms)) if quick_ms != null else "—", qc, 13), 66)
	_row_cell(row, _make_lbl(("%d ms" % int(real_ms))  if real_ms  != null else "—", rc, 13), 78)
	_row_cell(row, _make_score_badge(int(score) if score != null else 0), 52)

	var config_text := str(result.get("config", ""))
	var is_saved    := _has_config(_favorite_results, config_text)
	var actions     := HBoxContainer.new()
	actions.alignment = BoxContainer.ALIGNMENT_END
	actions.add_theme_constant_override("separation", 4)
	actions.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	var am := MarginContainer.new()
	am.add_theme_constant_override("margin_right", 8)
	am.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	am.add_child(actions)
	row.add_child(am)

	var copy_btn := _make_action_btn(_t("copy"), C_DIM)
	copy_btn.pressed.connect(_on_copy_pressed.bind(config_text))
	actions.add_child(copy_btn)

	if _active_nav != 2:
		var save_clr: Color = C_GREEN if is_saved else Color("f59e0b")
		var save_btn := _make_action_btn(_t("unsave") if is_saved else _t("save"), save_clr)
		save_btn.pressed.connect(_on_save_toggle.bind(config_text))
		actions.add_child(save_btn)
		var block_btn := _make_action_btn(_t("block"), Color("ef4444"))
		block_btn.pressed.connect(_on_block_toggle.bind(config_text))
		actions.add_child(block_btn)
	else:
		var unblock_btn := _make_action_btn(_t("unblock"), C_ORANGE)
		unblock_btn.pressed.connect(_on_block_toggle.bind(config_text))
		actions.add_child(unblock_btn)

	var open_btn := _make_action_btn(_t("open_hiddify"), Color.WHITE)
	open_btn.add_theme_stylebox_override("normal", _box(C_ACCENT, Color(0,0,0,0), 6))
	open_btn.add_theme_stylebox_override("hover", _box(C_ACCENT.lightened(0.15), Color(0,0,0,0), 6))
	open_btn.add_theme_stylebox_override("pressed", _box(C_ACCENT.darkened(0.1), Color(0,0,0,0), 6))
	open_btn.pressed.connect(_on_open_in_hiddify.bind(config_text))
	actions.add_child(open_btn)

	return panel


func _row_cell(row: HBoxContainer, child: Control, width: int) -> void:
	child.custom_minimum_size = Vector2(width, 0)
	child.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	row.add_child(child)


func _make_lbl(text: String, color: Color, size: int) -> Label:
	var lbl := Label.new()
	lbl.text = text
	lbl.add_theme_color_override("font_color", color)
	lbl.add_theme_font_size_override("font_size", size)
	lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	lbl.clip_text = true
	return lbl


func _make_working_badge(source_kind: String = "fresh", verification_tier: String = "live_confirmed", quality_tier: String = "unknown") -> Control:
	var c := CenterContainer.new()
	var s := StyleBoxFlat.new()
	var badge_color := C_GREEN
	var source_text := _t("fresh_badge")
	match verification_tier:
		"seed_confirmed":
			badge_color = C_BLUE
			source_text = _t("seed_badge")
		"history_retained":
			badge_color = C_ACCENT2
			source_text = _t("history_badge")
		"seed_unconfirmed":
			badge_color = C_ORANGE
			source_text = _t("unconfirmed_badge")
		_:
			if source_kind != "fresh":
				badge_color = C_ACCENT2
				source_text = _t("history_badge")
	s.bg_color = Color(badge_color.r, badge_color.g, badge_color.b, 0.12)
	s.border_color = Color(badge_color.r, badge_color.g, badge_color.b, 0.35)
	s.border_width_left = 1
	s.border_width_top = 1
	s.border_width_right = 1
	s.border_width_bottom = 1
	s.corner_radius_top_left = 10
	s.corner_radius_top_right = 10
	s.corner_radius_bottom_right = 10
	s.corner_radius_bottom_left = 10
	s.content_margin_left = 8
	s.content_margin_right = 8
	s.content_margin_top = 3
	s.content_margin_bottom = 3
	var inner := PanelContainer.new()
	inner.add_theme_stylebox_override("panel", s)
	var lbl := Label.new()
	lbl.text = "%s • %s" % [source_text, quality_tier.to_upper()]
	lbl.add_theme_font_size_override("font_size", 10)
	lbl.add_theme_color_override("font_color", badge_color)
	inner.add_child(lbl)
	c.add_child(inner)
	return c


func _make_protocol_badge(protocol: String) -> Control:
	var c := CenterContainer.new()
	var color: Color = PROTOCOL_COLORS.get(protocol, C_MUTED)
	var s := StyleBoxFlat.new()
	s.bg_color = Color(color.r, color.g, color.b, 0.14)
	s.border_color = Color(color.r, color.g, color.b, 0.3)
	s.border_width_left = 1
	s.border_width_top = 1
	s.border_width_right = 1
	s.border_width_bottom = 1
	s.corner_radius_top_left = 10
	s.corner_radius_top_right = 10
	s.corner_radius_bottom_right = 10
	s.corner_radius_bottom_left = 10
	s.content_margin_left = 8
	s.content_margin_right = 8
	s.content_margin_top = 3
	s.content_margin_bottom = 3
	var inner := PanelContainer.new()
	inner.add_theme_stylebox_override("panel", s)
	var lbl := Label.new()
	lbl.text = protocol.to_upper()
	lbl.add_theme_font_size_override("font_size", 10)
	lbl.add_theme_color_override("font_color", color)
	inner.add_child(lbl)
	c.add_child(inner)
	return c


func _make_score_badge(score_val: int) -> Control:
	var c := CenterContainer.new()
	var badge := PanelContainer.new()
	var score_color: Color
	if score_val >= 90:
		score_color = C_GREEN
	elif score_val >= 70:
		score_color = Color("22d3ee")
	elif score_val >= 50:
		score_color = C_ORANGE
	else:
		score_color = C_MUTED
	var bs := StyleBoxFlat.new()
	bs.bg_color = Color(score_color.r, score_color.g, score_color.b, 0.18)
	bs.border_color = Color(score_color.r, score_color.g, score_color.b, 0.4)
	bs.border_width_left = 1
	bs.border_width_top = 1
	bs.border_width_right = 1
	bs.border_width_bottom = 1
	bs.corner_radius_top_left = 12
	bs.corner_radius_top_right = 12
	bs.corner_radius_bottom_right = 12
	bs.corner_radius_bottom_left = 12
	bs.content_margin_left = 6
	bs.content_margin_right = 6
	bs.content_margin_top = 2
	bs.content_margin_bottom = 2
	badge.add_theme_stylebox_override("panel", bs)
	var lbl := Label.new()
	lbl.text = str(score_val) if score_val > 0 else "—"
	lbl.add_theme_font_size_override("font_size", 12)
	lbl.add_theme_color_override("font_color", score_color)
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	badge.add_child(lbl)
	c.add_child(badge)
	return c


func _make_action_btn(text: String, color: Color) -> Button:
	var btn := Button.new()
	btn.text = text
	btn.custom_minimum_size = Vector2(0, 28)
	btn.add_theme_font_size_override("font_size", 11)
	btn.add_theme_color_override("font_color", color)
	var ns := _box(Color(color.r, color.g, color.b, 0.08), Color(color.r, color.g, color.b, 0.2), 6)
	ns.content_margin_left = 8
	ns.content_margin_right = 8
	ns.content_margin_top = 2
	ns.content_margin_bottom = 2
	var hs := _box(Color(color.r, color.g, color.b, 0.2), Color(color.r, color.g, color.b, 0.4), 6)
	hs.content_margin_left = 8
	hs.content_margin_right = 8
	hs.content_margin_top = 2
	hs.content_margin_bottom = 2
	var ps := _box(Color(color.r, color.g, color.b, 0.32), Color(color.r, color.g, color.b, 0.5), 6)
	ps.content_margin_left = 8
	ps.content_margin_right = 8
	ps.content_margin_top = 2
	ps.content_margin_bottom = 2
	btn.add_theme_stylebox_override("normal", ns)
	btn.add_theme_stylebox_override("hover", hs)
	btn.add_theme_stylebox_override("pressed", ps)
	btn.pressed.connect(_anim_btn_press.bind(btn))
	return btn


func _get_flag(country: String) -> String:
	return COUNTRY_FLAGS.get(country, "🌐")


# =====================================================================
# FILTERS
# =====================================================================

func _rebuild_country_filter() -> void:
	_country_filter.clear()
	_country_filter.add_item(_t("all_countries"))
	var countries := PackedStringArray()
	for r in _all_results:
		var c := str(r.get("exit_country", r.get("region", "")))
		if c != "" and not countries.has(c):
			countries.append(c)
	countries.sort()
	for c in countries:
		_country_filter.add_item(c)


func _rebuild_protocol_filter() -> void:
	_protocol_filter.clear()
	_protocol_filter.add_item(_t("all_protocols"))
	var protos := PackedStringArray()
	for r in _all_results:
		var p := str(r.get("protocol", "")).to_lower()
		if p != "" and not protos.has(p):
			protos.append(p)
	protos.sort()
	for p in protos:
		_protocol_filter.add_item(p.to_upper())


func _on_search_changed(text: String) -> void:
	_search_query = text
	_rebuild_table()


func _on_filter_changed(_idx: int) -> void:
	var ci := _country_filter.selected
	_filter_country = _country_filter.get_item_text(ci) if ci > 0 else ""
	var pi := _protocol_filter.selected
	_filter_protocol = _protocol_filter.get_item_text(pi).to_lower() if pi > 0 else ""
	_rebuild_table()


# =====================================================================
# PIPELINE
# =====================================================================

func _on_run_pressed() -> void:
	_start_pipeline("smart")


func _on_quick_recovery_pressed() -> void:
	_start_pipeline("quick_recovery")


func _start_pipeline(mode: String) -> void:
	if _pipeline_running:
		return
	_pipeline_mode = mode
	_pipeline_running = true
	_pipeline_stdout = ""
	_pipeline_pid = -1
	_last_pipeline_state_hash = ""
	_pipeline_start_time = Time.get_ticks_msec()
	_run_button.disabled = true
	if _quick_recovery_button != null:
		_quick_recovery_button.disabled = true
	_run_button.text = _t("stage_running")
	_stop_button.visible = true
	_stop_button.text = _t("stop_btn")
	_stage_label.text = _t("stage_running")
	_progress_bar.value = 2
	_stat_verified_label.text = "0"
	_stat_working_label.text = "0"
	_stat_success_label.text = "0"
	_footer_status.text = _t("stage_running")
	_footer_status.add_theme_color_override("font_color", C_ORANGE)
	_run_pipeline_process()


func _on_stop_pressed() -> void:
	if not _pipeline_running:
		return
	var stop_path := ProjectSettings.globalize_path(PIPELINE_STOP_FLAG)
	var stop_file := FileAccess.open(stop_path, FileAccess.WRITE)
	if stop_file != null:
		stop_file.store_string("stop")
	if _pipeline_pid > 0:
		OS.execute("cmd", ["/c", "taskkill", "/PID", str(_pipeline_pid), "/T", "/F"], [], true)
	_pipeline_running = false
	_pipeline_pid = -1
	_run_button.disabled = false
	if _quick_recovery_button != null:
		_quick_recovery_button.disabled = false
	_run_button.text = _t("run_btn")
	_stop_button.visible = false
	_stage_label.text = "Stopped"
	_progress_bar.value = 0
	_footer_status.text = "Stopped"
	_footer_status.add_theme_color_override("font_color", C_ORANGE)

func _run_pipeline_process() -> void:
	var python := _resolve_python_path()
	if python == "":
		_pipeline_stdout = "Python not found"
		_pipeline_running = false
		return
	var stop_path := ProjectSettings.globalize_path(PIPELINE_STOP_FLAG)
	if FileAccess.file_exists(stop_path):
		DirAccess.remove_absolute(stop_path)
	var state_path := ProjectSettings.globalize_path(PIPELINE_STATE_JSON)
	if FileAccess.file_exists(state_path):
		DirAccess.remove_absolute(state_path)
	var script := ProjectSettings.globalize_path(PIPELINE_SCRIPT)
	var args := [script, "--real-limit", str(int(_real_limit_spin.value)), "--mode", _pipeline_mode]
	var cf := _country_focus_input.text.strip_edges()
	if cf != "":
		args.append("--countries")
		args.append(cf)
	if _exclude_russia_check.button_pressed:
		args.append("--exclude-countries")
		args.append("Russia")
	_pipeline_pid = OS.create_process(python, args)
	if _pipeline_pid <= 0:
		_pipeline_running = false
		_run_button.disabled = false
		if _quick_recovery_button != null:
			_quick_recovery_button.disabled = false
		_run_button.text = _t("run_btn")
		_stop_button.visible = false
		_stage_label.text = "Failed to start pipeline"
		_progress_bar.value = 0
		_footer_status.text = "Failed to start pipeline"
		_footer_status.add_theme_color_override("font_color", C_RED)


func _resolve_python_path() -> String:
	for p in PYTHON_CANDIDATES:
		if p.begins_with("C:/") or p.begins_with("/"):
			if FileAccess.file_exists(p):
				return p
		else:
			return p
	return ""


func _poll_pipeline_state() -> void:
	var path := ProjectSettings.globalize_path(PIPELINE_STATE_JSON)
	if not FileAccess.file_exists(path):
		return
	var text := FileAccess.get_file_as_string(path)
	if text == _last_pipeline_state_hash:
		return
	_last_pipeline_state_hash = text
	var parsed = JSON.parse_string(text)
	if parsed == null or not parsed is Dictionary:
		return
	var state: Dictionary = parsed as Dictionary
	var status := str(state.get("status", ""))
	var stage := str(state.get("stage", ""))
	var message := str(state.get("message", ""))
	var checked_total := int(state.get("checked_total", 0))
	var fresh_total := int(state.get("fresh_live_total", state.get("fresh_recommended_total", state.get("fresh_working_total", state.get("fresh_passing_total", 0)))))
	var retained_total := int(state.get("retained_total", 0))
	var visible_total := int(state.get("visible_total", state.get("recommended_visible_total", retained_total + fresh_total)))
	var progress_value := float(state.get("progress", -1))
	_stage_label.text = message if message != "" else stage
	_stat_verified_label.text = str(checked_total)
	_stat_working_label.text = str(fresh_total)
	_stat_success_label.text = str(visible_total)
	if status == "completed":
		_pipeline_running = false
		_pipeline_pid = -1
		_run_button.disabled = false
		if _quick_recovery_button != null:
			_quick_recovery_button.disabled = false
		_run_button.text = _t("run_btn")
		_stop_button.visible = false
		_progress_bar.value = 100
		if fresh_total == 0 and visible_total == 0:
			_footer_status.text = _t("placeholder_none")
			_footer_status.add_theme_color_override("font_color", C_ORANGE)
		elif fresh_total == 0 and visible_total > 0:
			_footer_status.text = "Fresh: 0, showing retained/seed mix"
			_footer_status.add_theme_color_override("font_color", C_ORANGE)
		else:
			_footer_status.text = _t("all_ok")
			_footer_status.add_theme_color_override("font_color", C_GREEN)
		_load_latest_results()
	elif status == "stopped":
		_pipeline_running = false
		_pipeline_pid = -1
		_run_button.disabled = false
		if _quick_recovery_button != null:
			_quick_recovery_button.disabled = false
		_run_button.text = _t("run_btn")
		_stop_button.visible = false
		_progress_bar.value = 0
		_footer_status.text = "Stopped"
		_footer_status.add_theme_color_override("font_color", C_ORANGE)
	elif status == "running":
		if progress_value >= 0.0:
			_progress_bar.value = clamp(progress_value, 2.0, 95.0)
		else:
			_progress_bar.value = clamp(float(checked_total) / max(float(_real_limit_spin.value), 1.0) * 100.0, 5.0, 95.0)


# =====================================================================
# HIDDIFY
# =====================================================================

func _on_copy_pressed(config_text: String) -> void:
	DisplayServer.clipboard_set(config_text)
	_footer_status.text = _t("status_copy")
	_footer_status.add_theme_color_override("font_color", C_GREEN)


func _on_open_in_hiddify(config_text: String) -> void:
	var result := _find_result_by_config(config_text)
	var pretty_name := _build_pretty_profile_name(
		result if not result.is_empty() else {"protocol": "proxy", "exit_country": "Unknown"})
	var raw_config := str(result.get("config", ""))
	DisplayServer.clipboard_set(raw_config)
	if FileAccess.file_exists(POWERSHELL_EXE):
		_launch_hiddify_import_helper(str(result.get("endpoint", "")), pretty_name, raw_config)
		_footer_status.text = _t("status_opened")
		_footer_status.add_theme_color_override("font_color", C_GREEN)
	else:
		_footer_status.text = _t("status_no_hiddify")
		_footer_status.add_theme_color_override("font_color", C_ORANGE)


func _build_pretty_profile_name(result: Dictionary) -> String:
	var region   := str(result.get("exit_country", result.get("region", "Unknown"))).to_upper()
	var protocol := str(result.get("protocol", "proxy")).to_upper()
	return "Anfisa VPN | %s | %s" % [region, protocol]


func _launch_hiddify_import_helper(endpoint: String, pretty_name: String, raw_config: String) -> void:
	if endpoint == "":
		return
	var python_path := _resolve_python_path()
	var helper_path := ProjectSettings.globalize_path(HIDDIFY_IMPORT_HELPER_SCRIPT)
	OS.create_process(python_path, [helper_path, endpoint, pretty_name, raw_config])


func _find_result_by_config(config_text: String) -> Dictionary:
	for r in _all_results + _favorite_results:
		if str(r.get("config", "")) == config_text:
			return r
	return {}


# =====================================================================
# BLACKLIST / FAVORITES
# =====================================================================

func _on_save_toggle(config_text: String) -> void:
	var result := _find_result_by_config(config_text)
	if result.is_empty():
		return
	if _has_config(_favorite_results, config_text):
		_favorite_results = _favorite_results.filter(
			func(r): return str(r.get("config", "")) != config_text)
	else:
		_favorite_results.append(result)
	_save_array_file(FAVORITES_JSON, _favorite_results)
	_rebuild_table()


func _on_block_toggle(config_text: String) -> void:
	if _has_config(_blocked_results, config_text):
		_blocked_results = _blocked_results.filter(
			func(r): return str(r.get("config", "")) != config_text)
	else:
		var result := _find_result_by_config(config_text)
		if not result.is_empty():
			_blocked_results.append(result)
		else:
			_blocked_results.append({"config": config_text})
	_save_array_file(BLACKLIST_JSON, _blocked_results)
	_rebuild_table()


func _has_config(arr: Array, config_text: String) -> bool:
	for r in arr:
		if str(r.get("config", "")) == config_text:
			return true
	return false


func _load_local_lists() -> void:
	_favorite_results = _load_array_file(FAVORITES_JSON)
	_blocked_results  = _load_array_file(BLACKLIST_JSON)


func _load_array_file(res_path: String) -> Array:
	var p := ProjectSettings.globalize_path(res_path)
	if not FileAccess.file_exists(p):
		return []
	var f := FileAccess.open(p, FileAccess.READ)
	if f == null:
		return []
	var parsed = JSON.parse_string(f.get_as_text())
	f.close()
	if parsed is Array:
		return parsed as Array
	if parsed is Dictionary:
		var pd2: Dictionary = parsed as Dictionary
		var out: Array = []
		for cfg in pd2.get("configs", []):
			out.append({"config": cfg})
		return out
	return []


func _save_array_file(res_path: String, data: Array) -> void:
	var p := ProjectSettings.globalize_path(res_path)
	var f := FileAccess.open(p, FileAccess.WRITE)
	if f == null:
		return
	f.store_string(JSON.stringify(data, "\t"))
	f.close()
