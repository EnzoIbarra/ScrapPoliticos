# 📋 Tareas de Validación - Enzo

**Objetivo:** Localizar la URL exacta del "Equipo de Gobierno Actual" para cada municipio asignado.

### 📝 Instrucciones:
1. Entra a la web del municipio.
2. Busca la sección donde aparecen los **Concejales Actuales** (busca palabras clave: "Corporación", "Gobierno", "Pleno", "Concejales").
3. **Copia la URL exacta** de esa sección.
4. Verifica si hay **emails**:
   - ¿Están visibles?
   - ¿Están ocultos en un botón (mailto)?
   - ¿No hay emails?
5. Anota si la lista es texto (seleccionable) o una imagen (scan/foto).

### 📍 Tu Lista de Municipios (22):

| # | Municipio | Web Principal (Entrada) | ✅ URL CORRECTA (Pegar aquí) | 📧 Emails (Sí/No/Ocultos) | Notas |
|---|---       |---                       |---                            |---                        |---    |
| 1 | Agaete | www.agaete.es      |https://www.agaete.es/ayuntamiento/corporacion-municipal |Ocultos (mailto) |Requiere limpieza de comentarios HTML y expansión de mailto |

| 2 | Agüimes | www.aguimes.es    |https://aguimes.es/corporacion-municipal/ |Sí (mailto) |Botón "Escríbele" con mailto. |

| 3 | Artenara | www.artenara.es  |https://www.artenara.es/portal-ciudadano/grupo-de-gobierno/ |No |Solo nombres y cargos disponibles en esta sección. |

| 4 | Arucas | www.arucas.org     |https://www.arucas.org/modules.php?mod=portal&file=ver_gen&id=TkRnek13PT0= |Visibles (Texto) |Texto plano dentro de tablas HTML antiguas. |
 
| 5 | Firgas | www.firgas.es      |https://www.villadefirgas.es/el-ayuntamiento/ |Visibles (Enricher) |Requiere entrar al perfil (/team/). El código ya hace esto. |

| 6 | Gáldar | www.galdar.es      |https://www.galdar.es/organigrama-municipal-2023-2027/ |Visibles |⚠️ REVISAR EN 2027. La URL incluye el periodo de mandato.|

| 7 | Ingenio | www.ingenio.es    |https://ingenio.es/grupo-de-gobierno/ |Sí (mailto) |Emails directos en la lista principal (módulos Divi). |

| 8 | La Aldea de San Nicolás | www.laaldeadesannicolas.es |https://laaldeasanicolas.es/ayuntamiento/  |Sí (mailto) |Iconos de email con enlace mailto estándar. |

| 9 | Las Palmas de GC | www.laspalmasgc.es |https://www.laspalmasgc.es/es/ayuntamiento/areas-de-gobierno/| NO |Solo nombres y cargos disponibles en esta sección |

| 10 | Mogán | www.mogan.es | | |Bloqueo de ip |

| 11 | Moya | www.villademoya.es |https://www.villademoya.es/ayuntamiento/corporacion |No | Solo nombres y cargos. No publican emails.|

| 12 | San Bartolomé de Tirajana | www.maspalomas.com |https://www.maspalomas.com/mnuayto-grupogobierno |Sí (mailto) |Emails en botones de icono (UIkit), scrapeables. |

| 13 | Santa Brígida | www.santabrigida.es |https://www.santabrigida.es/ayuntamiento/corporacion/equipo-gobierno-delegacion-areas/ |Sí (mailto) |Emails en iconos con enlace mailto estándar. |

| 14 | Santa Lucía de Tirajana | www.santaluciagc.com |https://www.santaluciagc.com/ayuntamiento/corporacion/ |No |Solo listado de nombres y cargos. |

| 15 | Santa María de Guía | www.santamariadeguia.es |https://santamariadeguia.es/corporacion-ayuntamiento-guia/ | No|Solo listado de nombres y cargos. |

| 16 | Tejeda | www.tejeda.es |https://tejeda.eu/corporacion-municipal/ |Sí (mailto) |Emails directos en la ficha. |

| 17 | Telde | www.telde.es |https://www.telde.es/ayuntamiento/areas-de-gobierno-y-concejalias-delegadas/ |Sí (mailto) | Botón "Contacto" funcional.|

| 18 | Teror | www.teror.es |https://teror.es/organizacion/grupo-de-gobierno-2023-2027/ |Sí (Texto) |Email visible en texto plano. URL caduca en 2027. |

| 19 | Valsequillo | www.valsequillogc.es |https://www.valsequillogc.es/ayto3/corporacion-2023-2027-2/ | Sí (mailto)|Icono de sobre con mailto. |

| 20 | Valleseco | www.valleseco.es |https://valleseco.es/valleseco/grupo-gobierno/ |Sí (Error) |Tienen un error tipográfico (mailto:http://...). El scraper lo limpiará. |

| 21 | Vega de San Mateo | www.vegasanmateo.es |https://www.vegadesanmateo.es/ayuntamiento/equipo-de-gobierno |Sí (mailto) |Emails claros en listado. |

| 22 | Arrecife | www.arrecife.es | |Posiblemente No |Web insegura.No se encontraron datos |