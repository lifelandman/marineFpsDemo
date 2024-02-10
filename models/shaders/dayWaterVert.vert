#version 150

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec3 p3d_Binormal;
in vec3 p3d_Tangent;
in vec2 p3d_MultiTexCoord0;

uniform struct p3d_LightSourceParameters
  { vec4 color

  ; vec4 ambient
  ; vec4 diffuse
  ; vec4 specular

  ; vec4 position

  ; vec3  spotDirection
  ; float spotExponent
  ; float spotCutoff
  ; float spotCosCutoff

  ; float constantAttenuation
  ; float linearAttenuation
  ; float quadraticAttenuation

  ; vec3 attenuation

  ; sampler2DShadow shadowMap

  ; mat4 shadowViewMatrix
  ;
  } p3d_LightSource[4];

out vec2 texCoord;

out vec4 shadowViewCoord[4];

out vec3 vertexNormal;
out vec3 binormal;
out vec3 tangent;

out vec4 vertexPos;

void main()
{
  vertexPos = p3d_ModelViewMatrix * p3d_Vertex;

  texCoord = p3d_MultiTexCoord0;
  vertexNormal = normalize(p3d_NormalMatrix * p3d_Normal);
  binormal = normalize(p3d_NormalMatrix * p3d_Binormal);
  tangent = normalize(p3d_NormalMatrix * p3d_Tangent);
  
  for ( int i = 0; i < p3d_LightSource.length(); ++i) {
   shadowViewCoord[i] = p3d_LightSource[i].shadowViewMatrix * vertexPos;
  }

  gl_Position = p3d_ProjectionMatrix * vertexPos;
}