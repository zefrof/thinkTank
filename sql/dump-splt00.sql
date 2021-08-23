-- MySQL dump 10.19  Distrib 10.3.29-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: database-1.cdoltwpzgxgp.us-east-2.rds.amazonaws.com    Database: magic
-- ------------------------------------------------------
-- Server version	10.2.21-MariaDB-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `archetypeToDeck`
--

DROP TABLE IF EXISTS `archetypeToDeck`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `archetypeToDeck` (
  `archetypeId` int(11) NOT NULL,
  `deckId` int(11) NOT NULL,
  KEY `archetypeId_atd` (`archetypeId`),
  KEY `deckId_atd` (`deckId`),
  CONSTRAINT `archetypeId_atd` FOREIGN KEY (`archetypeId`) REFERENCES `archetypes` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `deckId_atd` FOREIGN KEY (`deckId`) REFERENCES `decks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `archetypeToDeck`
--

LOCK TABLES `archetypeToDeck` WRITE;
/*!40000 ALTER TABLE `archetypeToDeck` DISABLE KEYS */;
INSERT INTO `archetypeToDeck` VALUES (9,1),(2,2),(9,3),(3,4),(10,5),(24,6),(10,7),(4,8),(13,9),(4,10),(2,11),(7,12),(5,13),(20,14),(10,15),(28,16),(28,17),(9,18),(2,19),(11,20),(14,21),(5,22),(7,23),(3,24),(2,25),(10,26),(24,27),(24,28),(20,29),(25,30),(13,31),(20,32),(7,33),(6,34),(9,35),(8,36),(8,37),(6,38),(7,39),(26,40),(27,41),(19,42),(13,43),(7,44),(28,45),(4,46),(22,47),(18,48),(23,49),(29,50),(21,51),(28,52),(16,53),(4,54),(21,55),(20,56),(2,57),(23,58),(6,59),(7,60),(4,61),(20,62),(3,486),(13,487),(13,489),(13,490),(13,492),(5,493),(5,494),(4,500),(4,509),(9,512),(4,514),(3,517),(4,582),(30,407),(31,408),(32,409),(5,410),(32,411),(33,412),(34,413),(9,414),(35,415),(30,416),(35,417),(30,418),(36,419),(30,420),(23,421),(34,422),(27,423),(37,424),(30,425),(18,426),(36,427),(24,428),(30,429),(38,430),(23,431),(39,432),(23,433),(34,434),(24,435),(35,436),(30,437),(24,438),(19,439),(39,440),(20,441),(5,71),(5,72),(10,73),(4,76),(5,77),(11,78),(13,80),(5,83);
/*!40000 ALTER TABLE `archetypeToDeck` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `archetypes`
--

DROP TABLE IF EXISTS `archetypes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
