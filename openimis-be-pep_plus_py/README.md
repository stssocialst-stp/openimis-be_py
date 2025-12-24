# openIMIS Backend PEP+ Module

## Description

This module implements the PEP+ (Programa de Educação Positiva) system for managing educational sessions with families, including:

- Session planning (Ferramenta 1)
- Attendance registration (Ferramenta 2)
- Session execution tracking (Ferramenta 3)
- Session supervision (Ferramenta 4)
- District bimonthly reports (Ferramenta 5)
- Bimonthly supervision meetings (Ferramenta 6)
- Bimonthly supervision reports (Ferramenta 7)

## Features

- Full CRUD operations via GraphQL API
- Integration with core, location, and individual modules
- Business rule validations
- Comprehensive reporting
- Audit trail support

## Installation

```bash
pip install -e ../openimis-be-pep_plus_py/
```

Add to openimis.json:
```json
{
  "name": "pep_plus",
  "pip": "-e ../openimis-be-pep_plus_py/"
}
```

## License

GNU AGPL v3
