^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package pal_pro_gripper_description
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

1.12.5 (2026-05-31)
-------------------
* Merge branch 'add/mj_tag_properties' into 'humble-devel'
  Add MuJoCo tag properties for mujoco simulation
  See merge request robots/pal_pro_gripper!55
* Add MuJoCo tag properties for mujoco simulation
* Contributors: Sai Kishor Kothakota

1.12.4 (2026-04-21)
-------------------
* gripper initial_value reduced to 0.07 instead of 0.079
* Reduce the gripper opening position to avoid hit the joint limit when completely open
* Contributors: ileniaperrella

1.12.3 (2026-04-20)
-------------------
* Change the init value + change the lower limit temporally
* Contributors: thomas.peyrucain

1.12.2 (2026-04-20)
-------------------
* Remove extra state interfaces and gazebo plugin
* Contributors: Noel Jimenez

1.12.1 (2026-04-13)
-------------------

1.12.0 (2026-04-10)
-------------------
* Add support for new gazebo
* Add sim_type to ros2_control
* Contributors: Aina, thomaspeyrucain

1.11.5 (2026-03-19)
-------------------
* Add safety controller
* Contributors: thomas.peyrucain

1.11.4 (2026-02-11)
-------------------
* Fix transmissions dependencies
* Contributors: Aina

1.11.3 (2026-02-09)
-------------------
* adding description
* Fix a typo
* adding calibration_tool
* Contributors: silviamasiello

1.11.2 (2025-12-17)
-------------------
* fixing urdf gripper
* adding use_sim_time
* Contributors: susannamastromauro

1.11.1 (2025-12-01)
-------------------
* add build_depend condition for pal_pro_gripper_transmissions
* fixing depend
* adding dependence transmission
* Contributors: ileniaperrella, susannamastromauro

1.11.0 (2025-11-28)
-------------------
* changing mechanical reduction
* fix ros2control
* fixing values gripper
* changes ros2control
* fix xacro
* fixing gripper.transmission
* fixing pipeline
* Fixing urdf and ros2control
* adding changing
* changing limits joints
* fix
* Fixing limits joint
* Fixing pipeline
* Changing revolute joint limits
* Fixing urdf and ros2control
* Contributors: susannamastromauro

1.10.0 (2025-11-12)
-------------------
* fixing sim_type
* fix range gripper urdf
* Contributors: susannamastromauro

1.9.0 (2025-11-05)
------------------

1.8.0 (2025-10-15)
------------------
* adding grasping frame
* Contributors: Matteo Villani

1.7.2 (2025-10-08)
------------------

1.7.1 (2025-09-08)
------------------
* Fix logic error for transmission
* Contributors: David ter Kuile

1.7.0 (2025-09-05)
------------------
* Add missing sim_type xacro args
* changed world and mujoco xacro argument name
* changed xacro parameter name
* changed world launch argument name
* Improved mujoco description structure
* Improved mujoco launch arguments
* Restored to original argument implementation
* Improved mujoco description logic
* added mujoco_ros2_control command interface
* added mujoco_ros2_control plugin
* Added mujoco model description
* Added mujoco arguments
* added mj_tags xacro file
* Contributors: David ter Kuile, Ortisa Poci

1.6.1 (2025-08-05)
------------------
* Merge branch 'tpe/update_gripper_range' into 'humble-devel'
  Update range of gripper
  See merge request robots/pal_pro_gripper!28
* Update range of gripper
* Contributors: thomaspeyrucain

1.6.0 (2025-08-01)
------------------

1.5.2 (2025-06-26)
------------------
* Update griper base link Inertias
* Contributors: lurenaud

1.5.1 (2025-03-31)
------------------

1.5.0 (2025-01-16)
------------------
* Merge branch 'tpe/simplify-3d-model' into 'humble-devel'
  Simplify 3d meshes
  See merge request robots/pal_pro_gripper!24
* Simplify 3d meshes
* Contributors: thomas.peyrucain, thomaspeyrucain

1.4.0 (2024-11-05)
------------------

1.3.0 (2024-09-19)
------------------
* Merge branch 'omm/gripper_std' into 'humble-devel'
  Gripper standarization
  See merge request robots/pal_pro_gripper!21
* Gripper std and suggested changes
* Proper base origin and offset
* Gripper std with tool_changer new arg
* Contributors: davidterkuile, oscarmartinez

1.2.0 (2024-08-09)
------------------
* Update gripper joint limit based on new encoder reduction of 81
* Contributors: Aina

1.1.0 (2024-08-06)
------------------

1.0.6 (2024-07-19)
------------------
* Merge branch 'air/feat/create_simulation_pkg' into 'humble-devel'
  create simulation package
  See merge request robots/pal_pro_gripper!17
* create simulation package & changing gazebo launch files into this pkg
* Merge branch 'dtk/fix/remove-mimic-joint-interface' into 'humble-devel'
  Remove mimic joint hardware interfaces
  See merge request robots/pal_pro_gripper!16
* Remove mimic joint hardware interfaces
* Contributors: Aina, David ter Kuile, davidterkuile

1.0.5 (2024-04-23)
------------------
* Merge branch 'feat/controllers' into 'humble-devel'
  Add jtc controller & joint_state_broadcaster
  See merge request robots/pal_pro_gripper!14
* add standalone controller launch file
* add controller into gazebo simulation
* Contributors: Aina Irisarri, davidterkuile

1.0.4 (2024-03-21)
------------------
* Merge branch 'dtk/fix/restructure' into 'humble-devel'
  Dtk/fix/restructure
  See merge request robots/pal_pro_gripper!13
* Update copyright to 2024
* Fix use_sim_time arg and set to True for all simulations
* Add use_sim_time as common launch arg
* restructure launch files pal_pro_gripper_description
* Contributors: David ter Kuile, Noel Jimenez, davidterkuile

1.0.3 (2024-03-11)
------------------
* Merge branch 'dtk/fix/mimic-join-hack' into 'humble-devel'
  Dtk/fix/mimic join hack
  See merge request robots/pal_pro_gripper!10
* Remove commented lines
* Add dummy link for the mimic joints
* Slight refactor of mimic joint ros2 control
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
* Merge branch 'fix-collision' into 'humble-devel'
  Fix collision
  See merge request robots/pal_pro_gripper!8
* simplify the root link adding a world link
* fix collision of the little box support
* Contributors: Adria Roig, ileniaperrella

1.0.0 (2024-01-29)
------------------
* Merge branch 'fix-spawn' into 'humble-devel'
  add world_link to improve the spawn in simulation
  See merge request robots/pal_pro_gripper!7
* add world_link to improve the spawn in simulation
* Merge branch 'ros2-migration' into 'humble-devel'
  Ros2 migration
  See merge request robots/pal_pro_gripper!5
* add working mimic joint configuration
* box support for the gripper reduced
* fix typo
* clean gazebo.urdf.xacro adding gazebo_ros2_control
* pal_gazebo_worlds exc_depend added
* update to 3.8 the cmake_minimum_required Version
* fix deg_to_rad extension
* add mimic joint for outer_finger_left_joint
* comment mimic joint gazebo plugin
* update show launch with rviz_config file
* working version of the pal_pro_gripper
* clean conf files pal_pro_gripper_description
* gripper transmission file modified
* fix name error in the ros2_control.xacro
* delete not necessary dependencies
* delete commented lines
* added robot_state_publisher to the gazebo spawn
* standalone gazebo launch files
* launch files for the spawn of the gripper in visualization
* pal_pro_gripper_description pkg migration files
* gazebo.urdf.xacro with ros2 plugin
* report files that have not changed
* migration of CMakeLists.txt and package.xml to ros2
* Contributors: Adria Roig, ileniaperrella

0.0.3 (2023-10-23)
------------------
* Merge branch 'feat/use_urdf_utils' into 'main'
  Feat/use urdf utils
  See merge request robots/pal_pro_gripper!4
* remove materials to make use of pal_urdf_utils package
* Contributors: Jordan Palacios, thomaspeyrucain

0.0.2 (2023-07-11)
------------------

0.0.1 (2023-07-03)
------------------
* Update dependencies and tests
* Remove deprecated xacro --inorder from tests
* Merge branch 'create-urdf' into 'main'
  Create urdf
  See merge request robots/pal_pro_gripper!2
* Update joint limit after confirming with mechanics
* update joint limits
* Merge branch 'create-urdf' into 'main'
  Create urdf
  See merge request robots/pal_pro_gripper!1
* Update mimic joint direction
* Update gazebo launch file and urdf to start simulation
* Load materials in general robot instead of urdf
* Add materials again, update joint limits:
* Update pid gains
* Update mimicjoint and typos
* first commit adding description and urdf
* first commit adding description and urdf
* Contributors: David ter Kuile, davidterkuile
