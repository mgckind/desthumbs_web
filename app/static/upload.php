<?php
   $destination_path = getcwd().DIRECTORY_SEPARATOR;
 
   $result = 0;
 
   $target_path = $destination_path . basename( $_FILES['myfile']['name']);
 
   if(@move_uploaded_file($_FILES['myfile']['tmp_name'], $target_path)) {
      $result = 1;
   }
 
   sleep(1);
?>