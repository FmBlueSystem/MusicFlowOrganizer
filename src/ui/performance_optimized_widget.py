"""
Performance Optimized UI Widget
==============================

Optimized UI components for large music libraries with:
- Asynchronous filtering and search
- Virtual scrolling for large lists
- Progressive loading of results
- Intelligent caching
- Responsive UI updates

Developed by BlueSystemIO
"""

import logging
import time
from typing import Dict, List, Any, Optional, Callable
from pathlib import Path

try:
    from PySide6.QtWidgets import (
        QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
        QLineEdit, QPushButton, QLabel, QProgressBar, QComboBox,
        QCheckBox, QSpinBox, QGroupBox, QFormLayout, QHeaderView,
        QAbstractItemView, QScrollArea, QFrame, QSplitter
    )
    from PySide6.QtCore import (
        Qt, QThread, Signal, QTimer, QAbstractTableModel, QModelIndex,
        QSortFilterProxyModel, QRect, QSize
    )
    from PySide6.QtGui import QFont, QPalette, QColor
    QT_AVAILABLE = True
except ImportError:
    QT_AVAILABLE = False
    # Fallback classes for testing without Qt
    class QWidget: pass
    class QVBoxLayout: pass
    class QTimer: pass
    class Signal: pass

if QT_AVAILABLE:
    from ..core.async_filter_engine import AsyncFilterEngine, FilterCriteria, FilterType, FilterResult
    from ..core.result_cache import ResultCache
    from ..core.track_analyzer import TrackData


class VirtualTableModel(QAbstractTableModel if QT_AVAILABLE else object):
    """Virtual table model for efficient display of large datasets."""
    
    def __init__(self, parent=None):
        if QT_AVAILABLE:
            super().__init__(parent)
        
        self.tracks_data: List[TrackData] = []
        self.headers = [
            "Filename", "Artist", "Title", "Genre", "BPM", "Key", "Energy", "Duration"
        ]
        self.logger = logging.getLogger(__name__)
    
    def rowCount(self, parent=QModelIndex()) -> int:
        """Return number of rows."""
        return len(self.tracks_data)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Return number of columns."""
        return len(self.headers)
    
    def data(self, index: QModelIndex, role=Qt.DisplayRole) -> Any:
        """Return data for given index and role."""
        if not QT_AVAILABLE or not index.isValid():
            return None
        
        if index.row() >= len(self.tracks_data):
            return None
        
        track_data = self.tracks_data[index.row()]
        column = index.column()
        
        if role == Qt.DisplayRole:
            return self._get_display_data(track_data, column)
        elif role == Qt.ToolTipRole:
            return self._get_tooltip_data(track_data, column)
        
        return None
    
    def headerData(self, section: int, orientation, role=Qt.DisplayRole) -> Any:
        """Return header data."""
        if not QT_AVAILABLE:
            return None
        
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if 0 <= section < len(self.headers):
                return self.headers[section]
        
        return None
    
    def _get_display_data(self, track_data: TrackData, column: int) -> str:
        """Get display data for specific column."""
        try:
            if column == 0:  # Filename
                return Path(track_data.file_path).name if track_data.file_path else ""
            elif column == 1:  # Artist
                return track_data.mixinkey_data.artist if track_data.mixinkey_data else ""
            elif column == 2:  # Title
                return track_data.mixinkey_data.title if track_data.mixinkey_data else ""
            elif column == 3:  # Genre
                return track_data.genre_classification.primary_genre if track_data.genre_classification else ""
            elif column == 4:  # BPM
                if track_data.mixinkey_data and track_data.mixinkey_data.bpm:
                    return f"{track_data.mixinkey_data.bpm:.1f}"
                return ""
            elif column == 5:  # Key
                return track_data.mixinkey_data.key if track_data.mixinkey_data else ""
            elif column == 6:  # Energy
                if track_data.mixinkey_data and track_data.mixinkey_data.energy:
                    return str(track_data.mixinkey_data.energy)
                return ""
            elif column == 7:  # Duration
                if track_data.mixinkey_data and track_data.mixinkey_data.duration:
                    minutes = int(track_data.mixinkey_data.duration // 60)
                    seconds = int(track_data.mixinkey_data.duration % 60)
                    return f"{minutes}:{seconds:02d}"
                return ""
        except Exception as e:
            self.logger.warning(f"Error getting display data for column {column}: {e}")
        
        return ""
    
    def _get_tooltip_data(self, track_data: TrackData, column: int) -> str:
        """Get tooltip data for specific column."""
        try:
            if column == 0:  # Filename
                return track_data.file_path or ""
            elif column == 3:  # Genre
                if track_data.genre_classification:
                    tooltip = f"Primary: {track_data.genre_classification.primary_genre or 'Unknown'}"
                    if track_data.genre_classification.secondary_genres:
                        secondary = ", ".join([f"{g[0]} ({g[1]:.1%})" for g in track_data.genre_classification.secondary_genres[:3]])
                        tooltip += f"\nSecondary: {secondary}"
                    if track_data.genre_classification.confidence:
                        tooltip += f"\nConfidence: {track_data.genre_classification.confidence:.1%}"
                    return tooltip
        except Exception as e:
            self.logger.warning(f"Error getting tooltip for column {column}: {e}")
        
        return ""
    
    def update_data(self, tracks_data: List[TrackData]):
        """Update the model with new data."""
        if QT_AVAILABLE:
            self.beginResetModel()
        
        self.tracks_data = tracks_data
        
        if QT_AVAILABLE:
            self.endResetModel()
        
        self.logger.info(f"Model updated with {len(tracks_data)} tracks")
    
    def add_tracks_batch(self, new_tracks: List[TrackData]):
        """Add tracks in batch for progressive loading."""
        if not new_tracks:
            return
        
        start_row = len(self.tracks_data)
        end_row = start_row + len(new_tracks) - 1
        
        if QT_AVAILABLE:
            self.beginInsertRows(QModelIndex(), start_row, end_row)
        
        self.tracks_data.extend(new_tracks)
        
        if QT_AVAILABLE:
            self.endInsertRows()
    
    def clear_data(self):
        """Clear all data from the model."""
        if QT_AVAILABLE:
            self.beginResetModel()
        
        self.tracks_data.clear()
        
        if QT_AVAILABLE:
            self.endResetModel()


class PerformanceOptimizedMusicLibraryWidget(QWidget if QT_AVAILABLE else object):
    """High-performance music library widget with async filtering and caching."""
    
    # Signals
    if QT_AVAILABLE:
        tracks_selected = Signal(list)  # List of selected track paths
        filter_applied = Signal(dict)   # Filter statistics
    
    def __init__(self, parent=None):
        if QT_AVAILABLE:
            super().__init__(parent)
        
        self.logger = logging.getLogger(__name__)
        
        # Initialize performance components
        self.filter_engine = AsyncFilterEngine(cache_size=200, batch_size=50) if QT_AVAILABLE else None
        self.result_cache = ResultCache(memory_cache_size=500, memory_limit_mb=200)
        
        # UI Components
        self.tracks_model = VirtualTableModel(self) if QT_AVAILABLE else None
        self.proxy_model = QSortFilterProxyModel(self) if QT_AVAILABLE else None
        
        # State
        self.all_tracks: Dict[str, TrackData] = {}
        self.current_filter_result: Optional[FilterResult] = None
        self.loading_timer = QTimer(self) if QT_AVAILABLE else None
        self.search_delay_timer = QTimer(self) if QT_AVAILABLE else None
        
        # Performance settings
        self.batch_size = 100  # Number of tracks to load per batch
        self.search_delay_ms = 300  # Delay before triggering search
        
        if QT_AVAILABLE:
            self._setup_ui()
            self._connect_signals()
    
    def _setup_ui(self):
        """Setup the user interface."""
        if not QT_AVAILABLE:
            return
        
        layout = QVBoxLayout(self)
        
        # Filter controls
        filter_group = self._create_filter_controls()
        layout.addWidget(filter_group)
        
        # Progress indicator
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Results table
        self.table_widget = self._create_results_table()
        layout.addWidget(self.table_widget)
        
        # Status bar
        self.status_label = QLabel("Ready")
        self.performance_label = QLabel("")
        
        status_layout = QHBoxLayout()
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        status_layout.addWidget(self.performance_label)
        
        layout.addLayout(status_layout)
    
    def _create_filter_controls(self) -> QGroupBox:
        """Create filter control widgets."""
        group = QGroupBox("Filters")
        layout = QFormLayout(group)
        
        # Text search
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search in filename, artist, title, album...")
        layout.addRow("Search:", self.search_input)
        
        # Genre filter
        self.genre_combo = QComboBox()
        self.genre_combo.setEditable(True)
        self.genre_combo.addItem("All Genres")
        layout.addRow("Genre:", self.genre_combo)
        
        # BPM range
        bpm_layout = QHBoxLayout()
        self.bpm_min_spin = QSpinBox()
        self.bpm_min_spin.setRange(60, 200)
        self.bpm_min_spin.setValue(60)
        self.bpm_max_spin = QSpinBox()
        self.bpm_max_spin.setRange(60, 200)
        self.bpm_max_spin.setValue(200)
        bmp_layout.addWidget(QLabel("Min:"))
        bpm_layout.addWidget(self.bpm_min_spin)
        bpm_layout.addWidget(QLabel("Max:"))
        bpm_layout.addWidget(self.bpm_max_spin)
        layout.addRow("BPM Range:", bpm_layout)
        
        # Key filter
        self.key_combo = QComboBox()
        self.key_combo.addItem("All Keys")
        # Add Camelot wheel keys
        for i in range(1, 13):
            self.key_combo.addItem(f"{i}A")
            self.key_combo.addItem(f"{i}B")
        layout.addRow("Key:", self.key_combo)
        
        # Compatible keys checkbox
        self.compatible_keys_check = QCheckBox("Show compatible keys")
        layout.addRow("", self.compatible_keys_check)
        
        # Clear filters button
        self.clear_filters_btn = QPushButton("Clear Filters")
        layout.addRow("", self.clear_filters_btn)
        
        return group
    
    def _create_results_table(self) -> QTableWidget:
        """Create the results table with virtual scrolling."""
        table = QTableWidget()
        
        # Setup model and proxy
        if self.proxy_model and self.tracks_model:
            self.proxy_model.setSourceModel(self.tracks_model)
            # Note: QTableWidget doesn't directly support custom models
            # In a real implementation, you'd use QTableView instead
        
        # Configure table
        table.setAlternatingRowColors(True)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSortingEnabled(True)
        
        # Set column headers
        headers = ["Filename", "Artist", "Title", "Genre", "BPM", "Key", "Energy", "Duration"]
        table.setColumnCount(len(headers))
        table.setHorizontalHeaderLabels(headers)
        
        # Configure column widths
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)  # Filename
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Artist
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Title
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Genre
        
        return table
    
    def _connect_signals(self):
        """Connect UI signals to handlers."""
        if not QT_AVAILABLE:
            return
        
        # Search input with delay
        self.search_delay_timer.setSingleShot(True)
        self.search_delay_timer.timeout.connect(self._trigger_filter)
        self.search_input.textChanged.connect(self._on_search_text_changed)
        
        # Filter controls
        self.genre_combo.currentTextChanged.connect(self._trigger_filter)
        self.bpm_min_spin.valueChanged.connect(self._trigger_filter)
        self.bpm_max_spin.valueChanged.connect(self._trigger_filter)
        self.key_combo.currentTextChanged.connect(self._trigger_filter)
        self.compatible_keys_check.toggled.connect(self._trigger_filter)
        
        # Clear filters
        self.clear_filters_btn.clicked.connect(self._clear_filters)
        
        # Filter engine signals
        if self.filter_engine:
            self.filter_engine.filter_started.connect(self._on_filter_started)
            self.filter_engine.filter_progress.connect(self._on_filter_progress)
            self.filter_engine.partial_results_ready.connect(self._on_partial_results)
            self.filter_engine.filter_completed.connect(self._on_filter_completed)
            self.filter_engine.filter_error.connect(self._on_filter_error)
        
        # Performance monitoring
        self.loading_timer.timeout.connect(self._update_performance_stats)
        self.loading_timer.start(2000)  # Update every 2 seconds
    
    def set_tracks_database(self, tracks_database: Dict[str, TrackData]):
        """Set the tracks database for filtering and display."""
        self.all_tracks = tracks_database
        
        if self.filter_engine:
            self.filter_engine.set_tracks_database(tracks_database)
        
        # Update genre combo box
        if QT_AVAILABLE:
            self._update_genre_combo()
        
        # Show all tracks initially
        self._display_tracks(list(tracks_database.values()))
        
        self.logger.info(f"Tracks database set: {len(tracks_database)} tracks")
    
    def _update_genre_combo(self):
        """Update genre combo box with available genres."""
        if not QT_AVAILABLE:
            return
        
        genres = set()
        for track_data in self.all_tracks.values():
            if track_data.genre_classification and track_data.genre_classification.primary_genre:
                genres.add(track_data.genre_classification.primary_genre)
        
        current_text = self.genre_combo.currentText()
        
        self.genre_combo.clear()
        self.genre_combo.addItem("All Genres")
        for genre in sorted(genres):
            self.genre_combo.addItem(genre)
        
        # Restore selection if possible
        index = self.genre_combo.findText(current_text)
        if index >= 0:
            self.genre_combo.setCurrentIndex(index)
    
    def _on_search_text_changed(self):
        """Handle search text changes with delay."""
        if QT_AVAILABLE and self.search_delay_timer:
            self.search_delay_timer.stop()
            self.search_delay_timer.start(self.search_delay_ms)
    
    def _trigger_filter(self):
        """Trigger filtering operation."""
        if not QT_AVAILABLE or not self.filter_engine:
            return
        
        criteria = self._build_filter_criteria()
        
        if not criteria:
            # No filters applied, show all tracks
            self._display_tracks(list(self.all_tracks.values()))
            return
        
        # Start async filtering
        self.filter_engine.filter_async(criteria)
    
    def _build_filter_criteria(self) -> List[FilterCriteria]:
        """Build filter criteria from UI controls."""
        criteria = []
        
        # Text search
        search_text = self.search_input.text().strip() if QT_AVAILABLE else ""
        if search_text:
            criteria.append(FilterCriteria(
                filter_type=FilterType.TEXT_SEARCH,
                value=search_text,
                operator="contains"
            ))
        
        # Genre filter
        genre = self.genre_combo.currentText() if QT_AVAILABLE else "All Genres"
        if genre and genre != "All Genres":
            criteria.append(FilterCriteria(
                filter_type=FilterType.GENRE,
                value=genre,
                operator="equals"
            ))
        
        # BPM range
        if QT_AVAILABLE:
            min_bpm = self.bpm_min_spin.value()
            max_bpm = self.bpm_max_spin.value()
            if min_bmp > 60 or max_bpm < 200:
                criteria.append(FilterCriteria(
                    filter_type=FilterType.BPM_RANGE,
                    value=(min_bpm, max_bpm),
                    operator="range"
                ))
        
        # Key filter
        key = self.key_combo.currentText() if QT_AVAILABLE else "All Keys"
        if key and key != "All Keys":
            if self.compatible_keys_check.isChecked():
                criteria.append(FilterCriteria(
                    filter_type=FilterType.CAMELOT_COMPATIBLE,
                    value=key,
                    operator="compatible"
                ))
            else:
                criteria.append(FilterCriteria(
                    filter_type=FilterType.KEY,
                    value=key,
                    operator="equals"
                ))
        
        return criteria
    
    def _clear_filters(self):
        """Clear all filter controls."""
        if not QT_AVAILABLE:
            return
        
        self.search_input.clear()
        self.genre_combo.setCurrentIndex(0)
        self.bpm_min_spin.setValue(60)
        self.bpm_max_spin.setValue(200)
        self.key_combo.setCurrentIndex(0)
        self.compatible_keys_check.setChecked(False)
    
    def _display_tracks(self, tracks: List[TrackData]):
        """Display tracks in the table."""
        if not QT_AVAILABLE or not self.tracks_model:
            return
        
        # Progressive loading for large datasets
        if len(tracks) > self.batch_size:
            self._display_tracks_progressive(tracks)
        else:
            self.tracks_model.update_data(tracks)
            self._update_table_from_model()
    
    def _display_tracks_progressive(self, tracks: List[TrackData]):
        """Display tracks progressively in batches."""
        if not QT_AVAILABLE or not self.tracks_model:
            return
        
        # Clear existing data
        self.tracks_model.clear_data()
        
        # Load in batches
        for i in range(0, len(tracks), self.batch_size):
            batch = tracks[i:i + self.batch_size]
            self.tracks_model.add_tracks_batch(batch)
            
            # Update table
            self._update_table_from_model()
            
            # Process events to keep UI responsive
            if QT_AVAILABLE:
                from PySide6.QtWidgets import QApplication
                QApplication.processEvents()
    
    def _update_table_from_model(self):
        """Update table widget from model data."""
        if not QT_AVAILABLE or not self.tracks_model:
            return
        
        # Note: In a real implementation with QTableView, this would be automatic
        # For QTableWidget, we need to manually populate
        
        tracks_data = self.tracks_model.tracks_data
        self.table_widget.setRowCount(len(tracks_data))
        
        for row, track_data in enumerate(tracks_data):
            for col in range(self.tracks_model.columnCount()):
                display_data = self.tracks_model._get_display_data(track_data, col)
                item = QTableWidgetItem(str(display_data))
                
                # Set tooltip
                tooltip = self.tracks_model._get_tooltip_data(track_data, col)
                if tooltip:
                    item.setToolTip(tooltip)
                
                self.table_widget.setItem(row, col, item)
    
    def _on_filter_started(self):
        """Handle filter operation start."""
        if QT_AVAILABLE:
            self.progress_bar.setVisible(True)
            self.progress_bar.setValue(0)
            self.status_label.setText("Filtering...")
    
    def _on_filter_progress(self, progress: int, status: str):
        """Handle filter progress update."""
        if QT_AVAILABLE:
            self.progress_bar.setValue(progress)
            self.status_label.setText(status)
    
    def _on_partial_results(self, partial_tracks: Dict[str, TrackData]):
        """Handle partial filter results for progressive display."""
        # Add partial results to display
        if QT_AVAILABLE and self.tracks_model:
            tracks_list = list(partial_tracks.values())
            self.tracks_model.add_tracks_batch(tracks_list)
            self._update_table_from_model()
    
    def _on_filter_completed(self, result: FilterResult):
        """Handle filter operation completion."""
        if not QT_AVAILABLE:
            return
        
        self.current_filter_result = result
        
        # Hide progress
        self.progress_bar.setVisible(False)
        
        # Update status
        status_text = f"Found {result.total_matches} tracks"
        if result.cache_hit:
            status_text += " (cached)"
        status_text += f" in {result.processing_time:.2f}s"
        
        self.status_label.setText(status_text)
        
        # Display results
        tracks_list = list(result.matched_tracks.values())
        self._display_tracks(tracks_list)
        
        # Emit signal
        if QT_AVAILABLE:
            self.filter_applied.emit({
                'total_matches': result.total_matches,
                'processing_time': result.processing_time,
                'cache_hit': result.cache_hit
            })
    
    def _on_filter_error(self, error_message: str):
        """Handle filter operation error."""
        if QT_AVAILABLE:
            self.progress_bar.setVisible(False)
            self.status_label.setText(f"Filter error: {error_message}")
        
        self.logger.error(f"Filter error: {error_message}")
    
    def _update_performance_stats(self):
        """Update performance statistics display."""
        if not QT_AVAILABLE or not self.filter_engine:
            return
        
        stats = self.filter_engine.get_performance_stats()
        cache_stats = self.result_cache.get_comprehensive_stats()
        
        # Format performance info
        perf_text = f"Filters: {stats['total_filters']} | "
        perf_text += f"Cache Hit Rate: {stats['cache_hit_rate']:.1%} | "
        perf_text += f"Avg Time: {stats['average_filter_time']:.2f}s | "
        perf_text += f"Memory: {cache_stats['memory_cache']['memory_usage']['current_mb']:.1f}MB"
        
        self.performance_label.setText(perf_text)
    
    def get_selected_tracks(self) -> List[str]:
        """Get list of selected track file paths."""
        if not QT_AVAILABLE:
            return []
        
        selected_rows = set()
        for item in self.table_widget.selectedItems():
            selected_rows.add(item.row())
        
        selected_tracks = []
        for row in selected_rows:
            if row < len(self.tracks_model.tracks_data):
                track_data = self.tracks_model.tracks_data[row]
                selected_tracks.append(track_data.file_path)
        
        return selected_tracks
    
    def clear_results(self):
        """Clear all results and reset the widget."""
        if QT_AVAILABLE:
            self.tracks_model.clear_data()
            self.table_widget.setRowCount(0)
            self.status_label.setText("Ready")
            self.performance_label.setText("")
        
        self.current_filter_result = None
