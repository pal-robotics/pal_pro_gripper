cmake_minimum_required(VERSION 3.8)
project(pal_pro_gripper_description)

find_package(ament_cmake_auto REQUIRED)
find_package(xacro REQUIRED)

ament_auto_find_build_dependencies()

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_python_install_package(${PROJECT_NAME})
ament_auto_package(INSTALL_TO_SHARE config robots launch mujoco meshes urdf ros2_control)
