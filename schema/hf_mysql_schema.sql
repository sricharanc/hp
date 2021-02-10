CREATE SCHEMA IF NOT EXISTS `hf` ;
USE `hf`;

DROP TABLE IF EXISTS `email_client`;

CREATE TABLE `email_client` (
  `email_client_id` int(11) NOT NULL AUTO_INCREMENT,
  `email_client_name` varchar(50) NOT NULL,
  PRIMARY KEY (`email_client_id`),
  UNIQUE KEY `email_client_name` (`email_client_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `email_account`;

CREATE TABLE `email_account` (
  `email_account_id` int(11) NOT NULL AUTO_INCREMENT,
  `email_address` varchar(320) NOT NULL,
  `email_client_id` int(11) NOT NULL,
  `last_update_id` varchar(200) DEFAULT NULL,
  `created_datetime` datetime NOT NULL,
  `message_download` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`email_account_id`),
  UNIQUE KEY `email_address` (`email_address`),
  KEY `fk_email_client_id` (`email_client_id`),
  CONSTRAINT `fk_email_client_id` FOREIGN KEY (`email_client_id`) REFERENCES `email_client` (`email_client_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8

DROP TABLE IF EXISTS `email_account_messages`;

CREATE TABLE `email_account_messages` (
  `email_account_messages_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `email_account_id` int(11) NOT NULL,
  `email_client_message_id` varchar(250) NOT NULL,
  `email_datetime` datetime DEFAULT NULL,
  PRIMARY KEY (`email_account_messages_id`),
  KEY `fk_email_account_id` (`email_account_id`),
  CONSTRAINT `fk_email_account_id` FOREIGN KEY (`email_account_id`) REFERENCES `email_account` (`email_account_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `email_message_components`;

CREATE TABLE `email_message_components` (
  `email_message_components_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `email_account_messages_id` bigint(20) NOT NULL,
  `component_type` enum('subject','from','to') NOT NULL,
  `component_value` varchar(2000) NOT NULL,
  PRIMARY KEY (`email_message_components_id`),
  KEY `fk_email_account_messages_id` (`email_account_messages_id`),
  CONSTRAINT `fk_email_account_messages_id` FOREIGN KEY (`email_account_messages_id`) REFERENCES `email_account_messages` (`email_account_messages_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `email_message_body`;

CREATE TABLE `email_message_body` (
  `email_account_messages_id` bigint(20) NOT NULL,
  `email_message` mediumtext NOT NULL,
  KEY `fk_email_message_body_email_account_messages_id` (`email_account_messages_id`),
  CONSTRAINT `fk_email_message_body_email_account_messages_id` FOREIGN KEY (`email_account_messages_id`) REFERENCES `email_account_messages` (`email_account_messages_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `filter_rules`;

CREATE TABLE `filter_rules` (
  `filter_rules_id` int(11) NOT NULL AUTO_INCREMENT,
  `rule_name` varchar(100) NOT NULL,
  `rule_value` text NOT NULL,
  PRIMARY KEY (`filter_rules_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `email_message_filter_rules_status`;

CREATE TABLE `email_message_filter_rules_status` (
  `email_account_messages_id` bigint(20) NOT NULL,
  `filter_rules_id` int(11) NOT NULL,
  KEY `fk_email_account_messages_id_email_message_filter_rules_status` (`email_account_messages_id`),
  KEY `fk_filter_rules_id_email_message_filter_rules_status` (`filter_rules_id`),
  CONSTRAINT `fk_email_account_messages_id_email_message_filter_rules_status` FOREIGN KEY (`email_account_messages_id`) REFERENCES `email_account_messages` (`email_account_messages_id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_filter_rules_id_email_message_filter_rules_status` FOREIGN KEY (`filter_rules_id`) REFERENCES `filter_rules` (`filter_rules_id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;