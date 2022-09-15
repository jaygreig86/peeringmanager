/*
SQLyog Ultimate v13.1.9 (64 bit)
MySQL - 10.3.36-MariaDB-log : Database - ipms
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
USE `ipms`;

/*Table structure for table `ipms_bgppeers` */

DROP TABLE IF EXISTS `ipms_bgppeers`;

CREATE TABLE `ipms_bgppeers` (
  `peerid` bigint(20) NOT NULL AUTO_INCREMENT,
  `asn` int(11) unsigned DEFAULT NULL,
  `description` varchar(128) DEFAULT NULL,
  `import` varchar(32) DEFAULT NULL,
  `export` varchar(32) DEFAULT NULL,
  `ipv4_limit` int(11) DEFAULT NULL,
  `ipv6_limit` int(11) DEFAULT NULL,
  PRIMARY KEY (`peerid`),
  UNIQUE KEY `asn` (`asn`)
) ENGINE=InnoDB AUTO_INCREMENT=121 DEFAULT CHARSET=utf8;

/*Table structure for table `ipms_bgpsessions` */

DROP TABLE IF EXISTS `ipms_bgpsessions`;

CREATE TABLE `ipms_bgpsessions` (
  `sessionid` bigint(20) NOT NULL AUTO_INCREMENT,
  `peerid` bigint(20) DEFAULT NULL,
  `address` varbinary(64) DEFAULT NULL,
  `type` enum('peer','customer') NOT NULL DEFAULT 'peer',
  `password` varchar(80) DEFAULT NULL,
  `routerid` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`sessionid`),
  UNIQUE KEY `address` (`address`),
  KEY `peerid` (`peerid`),
  CONSTRAINT `ipms_bgpsessions_ibfk_1` FOREIGN KEY (`peerid`) REFERENCES `ipms_bgppeers` (`peerid`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=365 DEFAULT CHARSET=utf8;

/*Table structure for table `ipms_logs` */

DROP TABLE IF EXISTS `ipms_logs`;

CREATE TABLE `ipms_logs` (
  `logid` bigint(20) NOT NULL AUTO_INCREMENT,
  `userid` bigint(20) NOT NULL,
  `logentry` blob DEFAULT NULL,
  `datetime` datetime DEFAULT NULL,
  `alert` tinyint(1) DEFAULT 0,
  `userip` varchar(64) DEFAULT NULL,
  `acknowledged` tinyint(4) DEFAULT 0,
  `type` enum('Error','Info','login') DEFAULT 'Info',
  PRIMARY KEY (`logid`),
  KEY `ipms_logs_ibfk_1` (`userid`),
  CONSTRAINT `ipms_logs_ibfk_1` FOREIGN KEY (`userid`) REFERENCES `ipms_users` (`userid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=59804 DEFAULT CHARSET=utf8;

/*Table structure for table `ipms_operations` */

DROP TABLE IF EXISTS `ipms_operations`;

CREATE TABLE `ipms_operations` (
  `opid` bigint(20) NOT NULL AUTO_INCREMENT,
  `data` varchar(255) DEFAULT NULL,
  `job` varchar(64) DEFAULT NULL,
  `date` datetime DEFAULT NULL,
  `status` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`opid`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8;

/*Table structure for table `ipms_routers` */

DROP TABLE IF EXISTS `ipms_routers`;

CREATE TABLE `ipms_routers` (
  `routerid` bigint(20) NOT NULL AUTO_INCREMENT,
  `routertypeid` bigint(20) DEFAULT NULL,
  `hostname` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`routerid`),
  UNIQUE KEY `hostname` (`hostname`),
  KEY `routertypeid` (`routertypeid`),
  CONSTRAINT `ipms_routers_ibfk_1` FOREIGN KEY (`routertypeid`) REFERENCES `ipms_routertypes` (`routertypeid`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=29 DEFAULT CHARSET=utf8;

/*Table structure for table `ipms_routertypes` */

DROP TABLE IF EXISTS `ipms_routertypes`;

CREATE TABLE `ipms_routertypes` (
  `routertypeid` bigint(20) NOT NULL AUTO_INCREMENT,
  `vendor` varchar(32) DEFAULT 'cisco',
  PRIMARY KEY (`routertypeid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8;

/*Table structure for table `ipms_settings` */

DROP TABLE IF EXISTS `ipms_settings`;

CREATE TABLE `ipms_settings` (
  `settingid` bigint(20) NOT NULL AUTO_INCREMENT,
  `key` varchar(255) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`settingid`)
) ENGINE=InnoDB AUTO_INCREMENT=8 DEFAULT CHARSET=utf8;

/*Table structure for table `ipms_users` */

DROP TABLE IF EXISTS `ipms_users`;

CREATE TABLE `ipms_users` (
  `userid` bigint(20) NOT NULL AUTO_INCREMENT,
  `username` varchar(64) DEFAULT NULL,
  `password` varchar(64) DEFAULT NULL,
  `usertype` enum('readonly','admin') DEFAULT NULL,
  PRIMARY KEY (`userid`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
