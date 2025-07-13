# 🤝 Guía de Contribución - MusicFlow Organizer

¡Gracias por tu interés en contribuir a MusicFlow Organizer! Esta guía te ayudará a empezar y hacer contribuciones efectivas.

## 🎯 Tipos de Contribuciones Buscadas

### 🐛 Corrección de Bugs
- Problemas de estabilidad en análisis de audio
- Issues de rendimiento con bibliotecas grandes
- Bugs de interfaz de usuario
- Problemas de compatibilidad multiplataforma

### ✨ Nuevas Características
- Mejoras en algoritmos de análisis de audio
- Nuevos esquemas de organización
- Integración con software DJ adicional
- Funcionalidades de playlist avanzadas

### 📖 Documentación
- Guías de usuario mejoradas
- Documentación técnica para desarrolladores
- Tutoriales y ejemplos
- Traducciones a otros idiomas

### 🧪 Testing
- Pruebas unitarias para módulos core
- Tests de integración
- Casos edge y escenarios de error
- Pruebas de rendimiento

## 🚀 Empezando

### 1. Configuración del Entorno

```bash
# Fork y clonar el repositorio
git clone https://github.com/tu-usuario/MusicFlowOrganizer.git
cd MusicFlowOrganizer

# Configurar entorno de desarrollo
make install
pre-commit install

# Verificar que todo funciona
make test
```

### 2. Estructura del Proyecto

```
MusicFlowOrganizer/
├── src/
│   ├── core/           # Lógica de negocio principal
│   ├── ui/             # Interfaz PySide6
│   ├── plugins/        # Sistema de plugins
│   └── audio/          # Procesamiento de audio
├── tests/
│   ├── unit/           # Pruebas unitarias
│   ├── integration/    # Pruebas de integración
│   └── fixtures/       # Datos de prueba
├── docs/               # Documentación
└── tools/              # Herramientas de desarrollo
```

### 3. Flujo de Desarrollo

```bash
# Crear rama para feature
git checkout -b feature/mi-nueva-caracteristica

# Hacer cambios y verificar calidad
make format
make lint
make test

# Commit con mensaje descriptivo
git commit -m "feat: agregar análisis de tempo variable"

# Push y crear PR
git push origin feature/mi-nueva-caracteristica
```

## 📋 Estándares de Código

### Formateo y Style
- **Black**: Formateo automático de código
- **isort**: Ordenamiento de imports
- **flake8**: Linting y style guide PEP8
- **mypy**: Verificación de tipos

```bash
# Aplicar formateo automático
make format

# Verificar style y tipos
make lint
```

### Convenciones de Naming
```python
# Clases: PascalCase
class AudioAnalyzer:
    pass

# Funciones y variables: snake_case
def analyze_audio_file(file_path: str) -> AudioResult:
    track_data = extract_metadata(file_path)
    return track_data

# Constantes: UPPER_SNAKE_CASE
SUPPORTED_FORMATS = ['.mp3', '.flac', '.wav']

# Archivos: snake_case.py
audio_analyzer.py
file_organizer.py
```

### Documentación de Código
```python
def analyze_audio_file(file_path: str, use_cache: bool = True) -> AudioAnalysisResult:
    """
    Analiza un archivo de audio para extraer características musicales.
    
    Args:
        file_path: Ruta absoluta al archivo de audio
        use_cache: Si usar caché para resultados previos
        
    Returns:
        AudioAnalysisResult con BPM, tonalidad, género y características
        
    Raises:
        AudioAnalysisError: Si el archivo no se puede procesar
        FileNotFoundError: Si el archivo no existe
        
    Example:
        >>> result = analyze_audio_file("/path/to/track.mp3")
        >>> print(f"BPM: {result.bpm}, Key: {result.key}")
    """
```

## 🧪 Pruebas

### Ejecutar Pruebas
```bash
# Suite completa
make test

# Pruebas específicas
pytest tests/unit/core/test_audio_analyzer.py
pytest tests/integration/test_mixinkey_integration.py

# Con cobertura
pytest --cov=src --cov-report=html
```

### Escribir Pruebas
```python
# tests/unit/core/test_audio_analyzer.py
import pytest
from src.core.audio_analyzer import AudioAnalyzer

class TestAudioAnalyzer:
    
    def test_bpm_detection_accuracy(self, audio_fixtures):
        """Test BPM detection con archivos conocidos."""
        analyzer = AudioAnalyzer()
        
        result = analyzer.analyze_file(audio_fixtures.house_128bpm)
        
        assert result.bpm == pytest.approx(128.0, abs=2.0)
        assert result.success is True
    
    def test_corrupted_file_handling(self, corrupted_audio_file):
        """Test manejo graceful de archivos corruptos."""
        analyzer = AudioAnalyzer()
        
        with pytest.raises(AudioAnalysisError):
            analyzer.analyze_file(corrupted_audio_file)
```

### Fixtures de Prueba
```python
# tests/conftest.py
@pytest.fixture
def audio_fixtures():
    """Proporciona archivos de audio para testing."""
    return AudioFixtures(
        house_128bpm="tests/fixtures/audio/house_128bpm.mp3",
        techno_135bpm="tests/fixtures/audio/techno_135bpm.wav",
        corrupted="tests/fixtures/audio/corrupted.mp3"
    )
```

## 🔧 Desarrollo de Plugins

### Estructura de Plugin
```python
# src/plugins/mi_plugin.py
from plugins.plugin_manager import BasePlugin

class MiCustomPlugin(BasePlugin):
    
    def __init__(self):
        super().__init__("mi_plugin", "1.0.0")
    
    def initialize(self, config: Dict[str, Any]) -> bool:
        """Inicializar plugin con configuración."""
        self.config = config
        return True
    
    def get_capabilities(self) -> List[str]:
        """Retornar capacidades del plugin."""
        return ["audio_analysis", "playlist_generation"]
    
    def analyze_track(self, file_path: str) -> Dict[str, Any]:
        """Análisis custom de pista."""
        # Implementación específica
        pass
```

### Registro de Plugin
```python
# Registrar plugin
from plugins.plugin_manager import plugin_manager

plugin_manager.register_plugin(MiCustomPlugin())
```

## 📝 Commit Messages

### Formato
```
tipo(scope): descripción corta

Descripción detallada opcional del cambio.

Fixes #123
```

### Tipos de Commit
- **feat**: Nueva característica
- **fix**: Corrección de bug  
- **docs**: Cambios en documentación
- **style**: Formateo, sin cambios de código
- **refactor**: Refactoring de código
- **test**: Agregar o modificar pruebas
- **chore**: Mantenimiento, updates de deps

### Ejemplos
```bash
feat(audio): agregar soporte para análisis de tempo variable

fix(ui): corregir freeze en filtrado de bibliotecas grandes

docs(api): actualizar documentación de AudioAnalyzer

test(core): agregar pruebas unitarias para FileOrganizer
```

## 🔍 Process de Review

### Antes de Enviar PR
- [ ] Código formateado con `make format`
- [ ] Linting pasando con `make lint`
- [ ] Todas las pruebas pasando con `make test`
- [ ] Documentación actualizada si es necesario
- [ ] Commit messages siguiendo convenciones
- [ ] Branch actualizado con main

### Checklist de PR
```markdown
## Descripción
Breve descripción de los cambios realizados.

## Tipo de Cambio
- [ ] Bug fix (cambio que corrige un issue)
- [ ] Nueva característica (cambio que agrega funcionalidad)
- [ ] Breaking change (cambio que afecta compatibilidad)
- [ ] Documentación

## Testing
- [ ] Pruebas existentes pasan
- [ ] Nuevas pruebas agregadas
- [ ] Probado manualmente

## Screenshots (si aplica)
[Agregar screenshots para cambios de UI]
```

## 🚀 Release Process

### Versioning
Seguimos [Semantic Versioning](https://semver.org/):
- **MAJOR**: Cambios incompatibles de API
- **MINOR**: Funcionalidad nueva compatible hacia atrás
- **PATCH**: Bug fixes compatibles hacia atrás

### Creación de Release
```bash
# Actualizar versión
poetry version patch  # o minor, major

# Crear tag
git tag v1.0.1
git push origin v1.0.1

# GitHub Actions creará release automáticamente
```

## 📚 Recursos Adicionales

### Documentación Técnica
- [Architecture Overview](docs/architecture.md)
- [API Reference](docs/api-reference.md)
- [Plugin Development Guide](docs/plugin-development.md)

### Herramientas de Desarrollo
- [Poetry](https://python-poetry.org/) - Gestión de dependencias
- [Pre-commit](https://pre-commit.com/) - Git hooks
- [pytest](https://pytest.org/) - Framework de testing
- [Black](https://black.readthedocs.io/) - Formateo de código

### Comunidad
- **Discord**: [BlueSystemIO Community](https://discord.gg/bluesystemio)
- **Forum**: [Discusiones Técnicas](https://community.bluesystemio.com)
- **Email**: dev@bluesystemio.com

## ❓ Preguntas Frecuentes

### ¿Cómo reportar un bug?
1. Verificar que no existe un issue similar
2. Crear nuevo issue con template de bug
3. Incluir pasos para reproducir, logs y entorno
4. Agregar label apropiado

### ¿Cómo proponer una nueva característica?
1. Abrir issue con template de feature request
2. Describir el problema que resuelve
3. Proponer solución con ejemplos
4. Discutir con mantenedores antes de implementar

### ¿Cómo contribuir sin saber programar?
- Reportar bugs y issues de usabilidad
- Mejorar documentación y guías
- Crear tutoriales y videos
- Traducir a otros idiomas
- Testing manual de nuevas características

---

¡Gracias por contribuir a MusicFlow Organizer! Tu ayuda hace que el software DJ sea mejor para toda la comunidad. 🎧

**BlueSystemIO Team**