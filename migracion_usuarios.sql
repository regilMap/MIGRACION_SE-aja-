-- ==================================================================
-- SCRIPT DE MIGRACIÓN DE USUARIOS A SISMAP_EDUCACION_M2
-- Generado automáticamente desde el documento Excel
-- ==================================================================

-- 1. REGISTRO DE MATCHES (Nombre -> CoedomId)
-- MATCH FIJO: 'Nombre y apellido' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Técnico de apoyo' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Tzaddi Javier' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Yokasta Noemí Cordero' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Rafelina Morel' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Carlos Candelario' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Elías Yanet Días' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Rafael Polanco Díaz' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Griselda Jiménez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Odalis Encarnación' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Elizabeth Núñez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Charityn Lantigua' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Ariani Sulay Cabrera' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Diomarys Virginia Manzanillo' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Julio Ramón Almonte' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Noemí Moya Santana' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Eufemia Gavilán B.' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Cruz María Rosario' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Iris Kenia E. Paulino' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Maribel Bastardos Paredes' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Nicodemo Abreu Sánchez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Témpora Aquino F.' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Dily Altagracia Calderón Rodríguez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Wellington Galván Castillo' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Belkis Esther Beato Villamán' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Cesilia Fabré' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Altagracia Rodríguez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Juana Rodríguez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Eduardo Rivas' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Nelson Miguel Castillo' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Carlos Liz Ramírez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Nombres y apellidos' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Sobeida Moronta' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Elvis Quirino García' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Jesús Peña Vásquez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Rober Mercedes' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Belkis García' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Miguel Ángel Del Valle' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Gabriela Javier' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'Luz Del Alba Gómez' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'CORREO' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'tzaddi.javier@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'yokasta.cordero@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'rafelina.morel@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'elias.diaz@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'griselda.jimenez@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'elizabeth.nunez@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'charityn.lantigua@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'diomarys.manzanillo@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'noemi.moya@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'cruz.rosario@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'maribel.bastardo@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'nicodemo.abreu@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'dily.calderon@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'welington.galvan@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'belkys.beato@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'altagracia.rodrigue1@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'eduardo.rivas@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FIJO: 'nelson.castillo@minerd.gob.do' (Rol: 4) -> CoedomId 98
-- MATCH FOUND: Búsqueda 'BARAHONA' -> 'Regional 01 Barahona' (CoedomId: 25187) usuario: Silverio Pérez García
-- MATCH FOUND: Búsqueda 'SAN JUAN' -> 'Regional 02 San Juan de la Maguana' (CoedomId: 25188) usuario: Fabio Ernesto Medina Moreta
-- MATCH FOUND: Búsqueda 'AZUA' -> 'Regional 03 Azua' (CoedomId: 25189) usuario: Juan Luis Beltré Ramírez
-- MATCH FOUND: Búsqueda 'BAHORUCO' -> 'Regional 18 Bahoruco' (CoedomId: 25202) usuario: Francsberth Hosmell Méndez Sena
-- MATCH FOUND: Búsqueda 'SAN PEDRO DE MACORIS' -> 'Regional 05 San Pedro de Macorís' (CoedomId: 25191) usuario: Viagney Ogilvis Ramirez Hodge
-- MATCH FOUND: Búsqueda 'HIGUEY' -> 'Regional 12 Higuey' (CoedomId: 25197) usuario: Edward  Cordero
-- MATCH FOUND: Búsqueda 'SAN CRISTOBAL' -> 'Distrito Educativo 04 03 San Cristóbal Sur' (CoedomId: 24916) usuario: Dorka Correa
-- MATCH FOUND: Búsqueda 'MONTE PLATA' -> 'Regional 17 Monte Plata' (CoedomId: 24996) usuario: Vicente Altagracia Fanith Snchez
-- MATCH FOUND: Búsqueda 'LA VEGA' -> 'Distrito Educativo 06 05 La Vega Este' (CoedomId: 24912) usuario: Carmen Marisol Leon Leon
-- MATCH FOUND: Búsqueda 'SAN FRANCISCO DE MACORIS' -> 'Regional 07 San Francisco de Macorís' (CoedomId: 25192) usuario: Yeralys del Carmen Hernández
-- MATCH FOUND: Búsqueda 'NAGUA' -> 'Regional 14 Nagua' (CoedomId: 25199) usuario: Geaovan Reynoso Pérez
-- MATCH FOUND: Búsqueda 'COTUI' -> 'Regional 16 Cotui' (CoedomId: 25201) usuario: Cecilio Santos Núñez
-- MATCH FOUND: Búsqueda 'SANTIAGO' -> 'Distrito Educativo 08 06 Santiago Noreste' (CoedomId: 24914) usuario: Deidy Elizabet Ortega Castro
-- MATCH FOUND: Búsqueda 'MAO' -> 'Regional 09 Mao' (CoedomId: 25194) usuario: Jairo Rodiguez
-- MATCH FOUND: Búsqueda 'PUERTO PLATA' -> 'Regional 11 Puerto Plata' (CoedomId: 25196) usuario: Humberto Francisco Batista Santos
-- MATCH FIJO: 'Nombres y apellidos' (Rol: 2) -> CoedomId 98
-- MATCH FIJO: 'Rober Mercedes' (Rol: 2) -> CoedomId 98
-- MATCH FIJO: 'Belkis García' (Rol: 2) -> CoedomId 98
-- MATCH FIJO: 'Miguel Ángel Del Valle' (Rol: 2) -> CoedomId 98
-- MATCH FIJO: 'Gabriela Javier' (Rol: 2) -> CoedomId 98
-- MATCH FIJO: 'Luz Del Alba Gómez' (Rol: 2) -> CoedomId 98

-- 2. USUARIOS NO ENCONTRADOS (Revisión Manual)
-- UNMATCHED: No se encontró distrito/regional para: 'TECNICO DISTRITAL' (Usuario: CORREO, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. Neuris Ramírez' (Usuario: neuris.ramirez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sra. Nina Almonte ' (Usuario: nina.almonte@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. Esmedin Eulogio Feliz Báez ' (Usuario: esmedin.feliz@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sra. Islanda Paniagua Offer' (Usuario: islanda.paniagua@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Rubén Ramírez' (Usuario: ruben.ramirezb@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sinailin Medina' (Usuario: sinailin.medina@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. Pilades Alberto Pérez Filpo ' (Usuario: pilades.perez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. Felix Beltré ' (Usuario: felix.beltreca@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. Juan Pascual Romero Santana ' (Usuario: juan.romeros@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Leosabeth María Recio Beltré' (Usuario: leosabeth.recio@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Braudilin Moquete Pérez ' (Usuario: braudilin.moquete@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Víctor Rocha Casilla ' (Usuario: victor.rocha@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Daysi Romery Méndez Morales' (Usuario: daysi.mendez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Heidy Feliz ' (Usuario: heidi.felix@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Danilo Antonio Osorio' (Usuario: danilo.osorio@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Noelia Alarcón López' (Usuario: noelia.alarcon@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Raúl de Jesús Sandoval' (Usuario: raul.sandoval@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Manuel Tucent Mateo   ' (Usuario: manuel.tucent@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Belta Santos' (Usuario: belta.santosab@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Raúl Polanco                 ' (Usuario: raul.polanco@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Dilenny Paredes                 ' (Usuario: dileny.paredes@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Elizabeth Palacio Linarez' (Usuario: elizabeth.palacio@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: ' Yeison Piña ' (Usuario: yeison.bocio@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Ana Julissa Polanco' (Usuario: ana.polancom@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Agustina Upia Montero' (Usuario: agustina.upiamo@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Daicy Fray Lebron ' (Usuario: deisy.lebron@docente.edu.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Angela González' (Usuario: angelar.gonzalez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Yocasta Paulino' (Usuario: yocasta.paulino@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Esteban Francis Dicent Ruiz ' (Usuario: esteban.dicent@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Genaro García' (Usuario: genaro.garcia@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Esther Morel  ' (Usuario: maria.morelp@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Yaneris del Rosario Forbes Lima   ' (Usuario: yaneris.forbes@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Geide Mercedes Ramírez Figuereo    ' (Usuario: geide.ramirez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Martha de Jesús  ' (Usuario: martha.dejesusm@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Vicente Fernández         ' (Usuario: vicente.fernandez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Henry Contreras    ' (Usuario: henry.contreras@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Mildred Rafaela Inoa Mañón    ' (Usuario: mildred.inoa@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Yancell Ferreras  ' (Usuario: yancell.ferrerasca@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Raysa Esther Del Pilar Rosario  ' (Usuario: raysa.rosario@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Nancy Herasme  ' (Usuario: nancy.herasme@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sofia Tejada Pérez de Martínez' (Usuario: sofia.tejada@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Jhojans Rudinelvi Díaz de la Cruz' (Usuario: jhojans.diaz@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Ydania Virginia Custodio Jorge' (Usuario: ydania.custodiojo@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Jovany Altagracia Díaz ' (Usuario: jovanny.diaz@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Jesús María Uribe Pérez' (Usuario: jesus.uribe@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Carlos Capellán Ramírez ' (Usuario: carlos.capellanra@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Ledwin Rafael Váldez' (Usuario: Ledwin.Valdez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Olga Lidia Jiménez ' (Usuario: sujey.martinez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Robinson Gil Durán ' (Usuario: robinson.gil@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Antonia Evangelista Rosario' (Usuario: antonia.rosario@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Alexis de Jesús ' (Usuario: alexis.dejesus@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Julio Ramón Calderón ' (Usuario: julio.calderonme@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'María Ysabel Taveras Rodríguez' (Usuario: maria.taverasro@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Arelis Del Rosario Martínez' (Usuario: arelis.delrosario@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Rosario Forchue Henrriquez ' (Usuario: rosario.forchue@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sra. Criselda Pérez Alcequiez.' (Usuario: criselda.perezal@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. Samuel Guzmán Reyes' (Usuario: samuel.reyes@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. Sandro de los Santos Drullard' (Usuario: sandro.delossantos@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Miosotty Eduvigis Rivas Jiménez' (Usuario: miosotty.rivas@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Francia Guerrero ' (Usuario: francia.guerrero@docente.edu.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Andrea Alvarez Nuñez ' (Usuario: andrea.alvarez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Rossanny López de Contreras' (Usuario: rossanny.lopez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Yohanny Mercedes Rodríguez Díaz' (Usuario: yohanny.rodriguezd@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Diógenes Martínez' (Usuario: diogenes.martinezsi1@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Tania Yocasta Martínez Peña' (Usuario: tania.martinez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Epifania Núñez Román' (Usuario: epifania.nunez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Francisco Flores ' (Usuario: francisco.flores@minerd.gobdo, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. José Vargas' (Usuario: jose.vargasg@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sr. Anyely González' (Usuario: anyely.gonzalez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'José Emilio Durán Lugo' (Usuario: jose.duranl@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Santiago Ovalles Bonilla' (Usuario: santiago.bonillas@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Sra. Magnolia Gómez ' (Usuario: ornelia.gomez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Rufino Antonio Reyes Gutiérrez' (Usuario: rufino.reyes@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'Germita J' (Usuario: germita.jimenez@minerd.gob.do, Rol: 4)
-- UNMATCHED: No se encontró distrito/regional para: 'REGIONAL EDUCATIVA' (Usuario: NOMBRE Y APELLIDOS, Rol: 8)
-- UNMATCHED: No se encontró distrito/regional para: 'REGIONAL 10 SANTO DOMINGO II' (Usuario: Alberto Veras, Rol: 8)
-- UNMATCHED: No se encontró distrito/regional para: 'REGIONAL 15 SANTO DOMINGO III' (Usuario: Adalgisa Garcia, Rol: 8)
-- UNMATCHED: No se encontró distrito/regional para: 'REGIONAL 13 MONTECRISTI' (Usuario: Pedro Isaias Pérez Peralta, Rol: 8)

-- 3. SCRIPTS DE INSERT
USE [SISMAP_EDUCACION_M2];
GO

INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Nombre y apellido', 'Dirección de Email', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Técnico de apoyo', 'Dirección de Email', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Tzaddi Javier', 'tzaddi.javier@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Yokasta Noemí Cordero', 'yokasta.cordero@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Rafelina Morel', 'rafelina.morel@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Carlos Candelario', 'carlos.candelariove@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Elías Yanet Días', 'elias.diaz@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Rafael Polanco Díaz', 'rafael.polanco@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Griselda Jiménez', 'griselda.jimenez@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Odalis Encarnación', 'odalis.encarnacion@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Elizabeth Núñez', 'elizabeth.nunez@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Charityn Lantigua', 'charityn.lantigua@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Ariani Sulay Cabrera', 'ariani.cabrera@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Diomarys Virginia Manzanillo', 'diomarys.manzanillo@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Julio Ramón Almonte', 'julio.almonte@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Noemí Moya Santana', 'noemi.moya@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Eufemia Gavilán B.', 'eufemia.gavilan@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Cruz María Rosario', 'cruz.rosario@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Iris Kenia E. Paulino', 'iris.paulino@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Maribel Bastardos Paredes', 'maribel.bastardo@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Nicodemo Abreu Sánchez', 'nicodemo.abreu@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Témpora Aquino F.', 'tempora.aquino@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Dily Altagracia Calderón Rodríguez', 'dily.calderon@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Wellington Galván Castillo', 'welington.galvan@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Belkis Esther Beato Villamán', 'belkys.beato@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Cesilia Fabré', 'cesilia.fabre@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Altagracia Rodríguez', 'altagracia.rodrigue1@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Juana Rodríguez', 'juana.rodriguezpe@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Eduardo Rivas', 'eduardo.rivas@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Nelson Miguel Castillo', 'nelson.castillo@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Carlos Liz Ramírez', 'carlos.liz@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Nombres y apellidos', 'Dirección de Email', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Sobeida Moronta', 'sobeida.moronta@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Elvis Quirino García', 'elvis.garcia@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Jesús Peña Vásquez', 'jesus.penav@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Rober Mercedes', 'rober.mercedes@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Belkis García', 'belkis.garcia@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Miguel Ángel Del Valle', 'miguel.delvalle@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Gabriela Javier', 'gabriela.javier@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Luz Del Alba Gómez', 'luz.gomezb@minerd.gob.do', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('CORREO', 'REGIONAL/ DISTRITO ASIGNADO', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('tzaddi.javier@minerd.gob.do', '06 La Vega', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('yokasta.cordero@minerd.gob.do', '07 San Francisco de Macorís', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('rafelina.morel@minerd.gob.do', '14  Nagua', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('elias.diaz@minerd.gob.do', '16  Cotuí', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('griselda.jimenez@minerd.gob.do', '08 Santiago', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('elizabeth.nunez@minerd.gob.do', '09 Mao', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('charityn.lantigua@minerd.gob.do', '11  Puerto Plata', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('diomarys.manzanillo@minerd.gob.do', '13 Montecristi', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('noemi.moya@minerd.gob.do', '05 San Pedro de Macorís', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('cruz.rosario@minerd.gob.do', '12  Higüey', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('maribel.bastardo@minerd.gob.do', '01 Barahona', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('nicodemo.abreu@minerd.gob.do', '02  San Juan', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('dily.calderon@minerd.gob.do', '03  Azua', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('welington.galvan@minerd.gob.do', '18 Bahoruco', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('belkys.beato@minerd.gob.do', '04  San Cristóbal', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('altagracia.rodrigue1@minerd.gob.do', '10 Santo Domingo II', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('eduardo.rivas@minerd.gob.do', '15  Santo Domingo III', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('nelson.castillo@minerd.gob.do', '17  Monte Plata', 4, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Silverio Pérez García', 'silverio.perez@minerd.gob.do', 8, 25187, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Fabio Ernesto Medina Moreta', 'fabio.medina@minerd.gob.do', 8, 25188, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Juan Luis Beltré Ramírez', 'juan.beltre@minerd.gob.do', 8, 25189, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Francsberth Hosmell Méndez Sena', 'francsberth.mendez@minerd.gob.do', 8, 25202, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Viagney Ogilvis Ramirez Hodge', 'viagney.ramirezho@minerd.gob.do', 8, 25191, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Edward  Cordero', 'edward.cordero@minerd.gob.do', 8, 25197, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Dorka Correa', 'dorka.correa@minerd.gob.do', 8, 24916, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Vicente Altagracia Fanith Snchez', 'vicenta.fanith@minerd.gob.do', 8, 24996, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Carmen Marisol Leon Leon', 'carmen.leon@minerd.gob.do', 8, 24912, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Yeralys del Carmen Hernández', 'yeralys.hernandez@minerd.gob.do', 8, 25192, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Geaovan Reynoso Pérez', 'geovan.reynoso@minerd.gob.do', 8, 25199, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Cecilio Santos Núñez', 'cecilio.santos@minerd.gob.do', 8, 25201, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Deidy Elizabet Ortega Castro', 'deidy.ortega@minerd.gob.do', 8, 24914, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Jairo Rodiguez', 'jairo.rodriguez@minerd.gob.do', 8, 25194, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Humberto Francisco Batista Santos', 'humberto.batista@minerd.gob.do', 8, 25196, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Nombres y apellidos', 'Correo', 2, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Rober Mercedes', 'rober.mercedes@minerd.gob.do', 2, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Belkis García', 'belkis.garcia@minerd.gob.do', 2, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Miguel Ángel Del Valle', 'miguel.delvalle@minerd.gob.do', 2, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Gabriela Javier', 'gabriela.javier@minerd.gob.do', 2, 98, 1, GETDATE());
INSERT INTO [Seguridad].[Usuarios] (Nombre, Correo, RolId, CoedomId, IsActive, CreatedAt) 
VALUES ('Luz Del Alba Gómez', 'luz.gomezb@minerd.gob.do', 2, 98, 1, GETDATE());
