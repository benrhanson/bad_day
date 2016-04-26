-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

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
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_name` VARCHAR(255) NULL,
  `password` VARCHAR(255) NULL,
  `email` VARCHAR(255) NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bad_day`.`stories`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bad_day`.`stories` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `story` VARCHAR(200) NULL,
  `thumbs_up` INT NULL,
  `thumbs_down` INT NULL,
  `user_id` INT NOT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_stories_users_idx` (`user_id` ASC),
  CONSTRAINT `fk_stories_users`
    FOREIGN KEY (`user_id`)
    REFERENCES `bad_day`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `bad_day`.`users_have_favorites`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `bad_day`.`users_have_favorites` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `users_id` INT NOT NULL,
  `stories_id` INT NOT NULL,
  `created_at` DATETIME NULL,
  `updated_at` DATETIME NULL,
  INDEX `fk_users_have_favorites_users1_idx` (`users_id` ASC),
  INDEX `fk_users_have_favorites_stories1_idx` (`stories_id` ASC),
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_users_have_favorites_users1`
    FOREIGN KEY (`users_id`)
    REFERENCES `bad_day`.`users` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_users_have_favorites_stories1`
    FOREIGN KEY (`stories_id`)
    REFERENCES `bad_day`.`stories` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
