^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package pal_pro_gripper_controller_configuration
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1.12.5 (2026-05-31)
-------------------

1.12.4 (2026-04-21)
-------------------

1.12.3 (2026-04-20)
-------------------

1.12.2 (2026-04-20)
-------------------

1.12.1 (2026-04-13)
-------------------
* Fixing open loop param
* Contributors: vivianamorlando

1.12.0 (2026-04-10)
-------------------

1.11.5 (2026-03-19)
-------------------

1.11.4 (2026-02-11)
-------------------

1.11.3 (2026-02-09)
-------------------

1.11.2 (2025-12-17)
-------------------

1.11.1 (2025-12-01)
-------------------

1.11.0 (2025-11-28)
-------------------
* fix xacro
* Fixing urdf and ros2control
* changing limits joints
* Fixing urdf and ros2control
* Contributors: susannamastromauro

1.10.0 (2025-11-12)
-------------------

1.9.0 (2025-11-05)
------------------
* Merge branch 'tpe/add_open_loop' into 'humble-devel'
  Add back openloop to controller
  See merge request robots/pal_pro_gripper!37
* Add back openloop to controller
* Contributors: thomas.peyrucain, thomaspeyrucain

1.8.0 (2025-10-15)
------------------

1.7.2 (2025-10-08)
------------------
* 100 hz to 1khz
* add update rate
* Contributors: Matteo Villani

1.7.1 (2025-09-08)
------------------

1.7.0 (2025-09-05)
------------------

1.6.1 (2025-08-05)
------------------

1.6.0 (2025-08-01)
------------------
* letting the srv to be launched as module
* let not it spawn 2 same controllers
* update deps
* cleaning
* solving
* pal_pro_gripper_grasp_check implemented in launch file
* Contributors: Matteo Villani

1.5.2 (2025-06-26)
------------------

1.5.1 (2025-03-31)
------------------
* Remove choices for end-effector side for triago compatibility
* Contributors: David ter Kuile

1.5.0 (2025-01-16)
------------------

1.4.0 (2024-11-05)
------------------
* Set update_rate for joint_state_broadcaster
* Contributors: Noel Jimenez

1.3.0 (2024-09-19)
------------------

1.2.0 (2024-08-09)
------------------

1.1.0 (2024-08-06)
------------------
* Use controller_type from the controllers config
* Contributors: Noel Jimenez

1.0.6 (2024-07-19)
------------------

1.0.5 (2024-04-23)
------------------
* Merge branch 'feat/controllers' into 'humble-devel'
  Add jtc controller & joint_state_broadcaster
  See merge request robots/pal_pro_gripper!14
* delete caster joints
* add joint_broadcaster controller directly in the standalone launch file
* add standalone controller launch file
* add controller into gazebo simulation
* add joint_state_broadcaster config
* Contributors: Aina Irisarri, davidterkuile

1.0.4 (2024-03-21)
------------------
* Merge branch 'dtk/fix/restructure' into 'humble-devel'
  Dtk/fix/restructure
  See merge request robots/pal_pro_gripper!13
* Update copyright to 2024
* Rename to pal_pro_gripper_controller.launch.py
* Restructure launch file controller_configurations
* Contributors: David ter Kuile, Noel Jimenez, davidterkuile

1.0.3 (2024-03-11)
------------------
* Merge branch 'dtk/fix/add-linter-tests' into 'humble-devel'
  Dtk/fix/add linter tests
  See merge request robots/pal_pro_gripper!11
* Add tests packages to package.xml
* Add linter tests in CMakeLists.txt
* Contributors: David ter Kuile, davidterkuile

1.0.2 (2024-03-06)
------------------

1.0.1 (2024-01-31)
------------------

1.0.0 (2024-01-29)
------------------
* Merge branch 'ros2-migration' into 'humble-devel'
  Ros2 migration
  See merge request robots/pal_pro_gripper!5
* delete type of the controller in the yaml
* add gazebo_controller_manager_cfg
* add missing exc_depends
* update to 3.8 the cmake_minimum_required Version
* clean package.xml file
* clean CMakeLists.txt and package of contr.conf.
* delete not necessary dependencies
* fix yaml file
* controller_configuration pkg migration
* migration of CMakeLists.txt and package.xml to ros2
* Contributors: Adria Roig, ileniaperrella

0.0.3 (2023-10-23)
------------------
* Merge branch 'feat/use_urdf_utils' into 'main'
  Feat/use urdf utils
  See merge request robots/pal_pro_gripper!4
* Remove gazebo package + tune grasp service
* Contributors: Jordan Palacios, thomaspeyrucain

0.0.2 (2023-07-11)
------------------

0.0.1 (2023-07-03)
------------------
* Merge branch 'create-urdf' into 'main'
  Create urdf
  See merge request robots/pal_pro_gripper!1
* add gripper wrapper and grasping service
* Add controller_config and controller_config gazebo
* Contributors: David ter Kuile, davidterkuile
