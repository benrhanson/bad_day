-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema bad_day
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema bad_day
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `bad_day` DEFAULT CHARACTER SET utf8 ;
USE `bad_day` ;

-- -----------------------------------------------------
-- Table `bad_day`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bad_day`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_name` VARCHAR(255) NULL DEFAULT NULL,
  `password` VARCHAR(255) NULL DEFAULT NULL,
  `email` VARCHAR(255) NULL DEFAULT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 12
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `bad_day`.`stories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bad_day`.`stories` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `story` VARCHAR(200) NULL DEFAULT NULL,
  `thumbs_up` INT(11) NULL DEFAULT NULL,
  `thumbs_down` INT(11) NULL DEFAULT NULL,
  `user_id` INT(11) NOT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_stories_users_idx` (`user_id` ASC),
  CONSTRAINT `fk_stories_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `bad_day`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 15
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `bad_day`.`users_have_favorites`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bad_day`.`users_have_favorites` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `story_id` INT(11) NOT NULL,
  `created_at` DATETIME NULL DEFAULT NULL,
  `updated_at` DATETIME NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_users_have_favorites_users1_idx` (`user_id` ASC),
  INDEX `fk_users_have_favorites_stories1_idx` (`story_id` ASC),
  CONSTRAINT `fk_users_have_favorites_stories1`
    FOREIGN KEY (`story_id`)
    REFERENCES `bad_day`.`stories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_have_favorites_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `bad_day`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 14
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `bad_day`.`users_have_votes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bad_day`.`users_have_votes` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `user_id` INT(11) NOT NULL,
  `story_id` INT(11) NOT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_users_have_voted_users1_idx` (`user_id` ASC),
  INDEX `fk_users_have_voted_stories1_idx` (`story_id` ASC),
  CONSTRAINT `fk_users_have_voted_stories1`
    FOREIGN KEY (`story_id`)
    REFERENCES `bad_day`.`stories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_have_voted_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `bad_day`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
AUTO_INCREMENT = 5
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `bad_day`.`users_send_condolences`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bad_day`.`users_send_condolences` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `story_id` INT(11) NOT NULL,
  `user_id` INT(11) NOT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_users_send_condolences_stories1_idx` (`story_id` ASC),
  INDEX `fk_users_send_condolences_users1_idx` (`user_id` ASC),
  CONSTRAINT `fk_users_send_condolences_stories1`
    FOREIGN KEY (`story_id`)
    REFERENCES `bad_day`.`stories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_send_condolences_users1`
    FOREIGN KEY (`user_id`)
    REFERENCES `bad_day`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
