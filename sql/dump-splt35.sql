/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subArchetypeToArchetype` (
  `subArchetypeId` int(11) NOT NULL,
  `archetypeId` int(11) NOT NULL,
  KEY `subArchetypeToArchetype_FK` (`subArchetypeId`),
  KEY `subArchetypeToArchetype_FK_1` (`archetypeId`),
  CONSTRAINT `subArchetypeToArchetype_FK` FOREIGN KEY (`subArchetypeId`) REFERENCES `subArchetypes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `subArchetypeToArchetype_FK_1` FOREIGN KEY (`archetypeId`) REFERENCES `archetypes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subArchetypeToArchetype`
--

LOCK TABLES `subArchetypeToArchetype` WRITE;
/*!40000 ALTER TABLE `subArchetypeToArchetype` DISABLE KEYS */;
INSERT INTO `subArchetypeToArchetype` VALUES (1,2),(2,11),(3,14),(4,5),(5,7),(6,3),(7,2),(8,10),(9,24),(10,20),(11,25),(12,13),(13,13),(14,6),(15,9),(16,8),(17,6),(18,7),(19,26),(20,27),(21,19),(22,13),(23,28),(24,4),(25,22),(26,18),(27,23),(28,29),(29,21),(30,28),(31,16),(32,4),(33,20),(34,2),(35,6),(36,7),(37,4),(38,20),(39,26),(40,30),(41,31),(42,32),(43,32),(44,33),(45,34),(46,9),(47,35),(48,30),(49,36),(50,30),(51,37),(52,24),(53,38),(56,39),(57,34),(58,24),(59,19),(60,39),(61,20),(62,42),(63,21);
/*!40000 ALTER TABLE `subArchetypeToArchetype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `subArchetypeToDeck`
--

DROP TABLE IF EXISTS `subArchetypeToDeck`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subArchetypeToDeck` (
  `subArchetypeId` int(11) NOT NULL,
  `deckId` int(11) NOT NULL,
  KEY `subArchetypeToDeck_FK` (`deckId`),
  KEY `subArchetypeToDeck_FK_1` (`subArchetypeId`),
  CONSTRAINT `subArchetypeToDeck_FK` FOREIGN KEY (`deckId`) REFERENCES `decks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `subArchetypeToDeck_FK_1` FOREIGN KEY (`subArchetypeId`) REFERENCES `subArchetypes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subArchetypeToDeck`
--

LOCK TABLES `subArchetypeToDeck` WRITE;
/*!40000 ALTER TABLE `subArchetypeToDeck` DISABLE KEYS */;
INSERT INTO `subArchetypeToDeck` VALUES (15,1),(7,2),(15,3),(6,4),(8,5),(9,6),(8,7),(32,8),(22,9),(32,10),(7,11),(36,12),(4,13),(38,14),(8,15),(23,16),(23,17),(15,18),(1,19),(2,20),(3,21),(4,22),(5,23),(6,24),(1,25),(8,26),(9,27),(9,28),(10,29),(11,30),(12,31),(10,32),(5,33),(14,34),(15,35),(16,36),(16,37),(14,38),(5,39),(39,40),(20,41),(21,42),(12,43),(5,44),(23,45),(24,46),(25,47),(26,48),(27,49),(28,50),(29,51),(23,52),(31,53),(24,54),(29,55),(10,56),(1,57),(27,58),(14,59),(5,60),(24,61),(10,62),(6,486),(22,487),(22,489),(22,490),(22,492),(4,493),(4,494),(32,500),(24,509),(15,512),(32,514),(6,517),(40,407),(41,408),(43,409),(4,410),(43,411),(44,412),(45,413),(46,414),(47,415),(48,416),(47,417),(48,418),(49,419),(50,420),(27,421),(45,422),(20,423),(51,424),(50,425),(26,426),(49,427),(52,428),(50,429),(53,430),(27,431),(56,432),(27,433),(57,434),(52,435),(47,436),(50,437),(58,438),(59,439),(60,440),(61,441),(4,72),(8,73),(32,76),(4,77),(2,78),(22,80),(4,71);
/*!40000 ALTER TABLE `subArchetypeToDeck` ENABLE KEYS */;
UNLOCK TABLES;

--
