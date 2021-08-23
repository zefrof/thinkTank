-- Table structure for table `subArchetypes`
--

DROP TABLE IF EXISTS `subArchetypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subArchetypes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `type` tinyint(1) NOT NULL DEFAULT 0,
  `active` tinyint(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=64 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `subArchetypes`
--

LOCK TABLES `subArchetypes` WRITE;
/*!40000 ALTER TABLE `subArchetypes` DISABLE KEYS */;
INSERT INTO `subArchetypes` VALUES (1,'Scapeshift',0,1),(2,'Merfolk',0,1),(3,'Hardened Scales',0,1),(4,'Boros Burn',0,1),(5,'4C Snowblade',0,1),(6,'Gifts Storm',0,1),(7,'Titan Field',0,1),(8,'Ponza',0,1),(9,'Mono-Red Blitz',0,1),(10,'Sultai Snow Control',0,1),(11,'Orzhov Aristocrats',0,1),(12,'Dredge Vine',0,1),(13,'Crab Vine',0,1),(14,'Jund Death\'s Shadow',0,1),(15,'Humans',0,1),(16,'Uroza',0,1),(17,'Mardu Death\'s Shadow',0,1),(18,'Azorius Stoneblade',0,1),(19,'Bant Soulherder',0,1),(20,'Dimir Inverter',0,1),(21,'Bant Bogles',0,1),(22,'Dredge',0,1),(23,'Temur Moon',0,1),(24,'Mono-Green Tron',0,1),(25,'Jund Goblins',0,1),(26,'Niv to Light',0,1),(27,'Rogue',0,1),(28,'Ad Nauseam',0,1),(29,'Eldrazi Taxes',0,1),(30,'Blue Moon',0,1),(31,'Jund',0,1),(32,'Eldrazi Tron',0,1),(33,'4C Snow Control',0,1),(34,'Titan Shift',0,1),(35,'Grixis Death\'s Shadow',0,1),(36,'Bant Snowblade',0,1),(37,'Mono-Blue Tron',0,1),(38,'Bant Snow Control',0,1),(39,'4C Soulherder',0,1),(40,'Azorius Superfriends',0,1),(41,'Naya Winota',0,1),(42,'Mono-Green Stompy',0,1),(43,'Golgari Stompy',0,1),(44,'Lotus Breach',0,1),(45,'Mono-White Devotion',0,1),(46,'Orzhov Humans',0,1),(47,'Gruul Midrange',0,1),(48,'Jeskai Superfriends',0,1),(49,'Ensoul Artifact',0,1),(50,'Esper Superfriends',0,1),(51,'Mono-Black Vampires',0,1),(52,'Izzet Spellslinger',0,1),(53,'Mono-Red Aggro',0,1),(56,'Simic Ramp',0,1),(57,'Azorius Devotion',0,1),(58,'Boros Feather',0,1),(59,'Orzhov Auras',0,1),(60,'Bant Ramp',0,1),(61,'Sultai Delirium',0,1),(62,'Mono-Black Aggro',0,1),(63,'Death and Taxes',0,1);
/*!40000 ALTER TABLE `subArchetypes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(45) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `lastLogin` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
