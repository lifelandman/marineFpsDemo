#version 150
uniform sampler2D p3d_Texture0;

uniform float osg_FrameTime;

uniform mat3 p3d_NormalMatrix;

uniform struct p3d_LightSourceParameters {
  // Primary light color.
  vec4 color;

  // Light color broken up into components, for compatibility with legacy
  // shaders.  These are now deprecated.
  vec4 ambient;
  vec4 diffuse;
  vec4 specular;

  // View-space position.  If w=0, this is a directional light, with the xyz
  // being -direction.
  vec4 position;

  // Spotlight-only settings
  vec3 spotDirection;
  float spotExponent;
  float spotCutoff;
  float spotCosCutoff;

  // Individual attenuation constants
  float constantAttenuation;
  float linearAttenuation;
  float quadraticAttenuation;

  // constant, linear, quadratic attenuation in one vector
  vec3 attenuation;

  // Shadow map for this light source
  sampler2DShadow shadowMap;

  // Transforms view-space coordinates to shadow map coordinates
  mat4 shadowViewMatrix;
} p3d_LightSource[4];

in vec2 texCoord;

in vec3 vertexNormal;
in vec3 binormal;
in vec3 tangent;

in vec4 vertexPos;
in vec4 shadowViewCoord[4];
out vec4 p3d_fragColor;


void main()
{
 vec4 newColor = vec4(0.0, 0.0, 0.0, 1.0);
 vec3 normal = normalize(vertexNormal);

 //calc new normals
 float frameTime = mod(osg_FrameTime, 120)/2.0;
 //float frameTime = 1.0;
 vec2 newTexCoord1 = vec2(texCoord.x * 10 - frameTime, texCoord.y * 10 + frameTime);
 vec2 newTexCoord2 = vec2(-texCoord.x * 9.5 + frameTime/2, texCoord.y * 9.5 + frameTime/2);
 
 vec3 normalA = (texture(p3d_Texture0, newTexCoord1).rgb * 2.0) - 1.0;
 vec3 normalB = (texture(p3d_Texture0, newTexCoord2).rgb * 2.0) - 1.0;
 vec3 newNormal = normalize((normalA + normalB)/2.0);

 float bneath = -0.9;
 float above = 0.9;
 if ( any(lessThan(vec3(bneath), newNormal)) && any(lessThan( newNormal, vec3(above) )) ) { 
 bvec3 truths1 = lessThan(vec3(bneath), newNormal);
 bvec3 truths2 = lessThan(newNormal, vec3(above));
 bvec3 truths = bvec3(truths1.x && truths2.x, truths1.y && truths2.y, truths1.z && truths2.z);
 if (truths.x) newNormal.x = 0.5;
 if (truths.y) newNormal.y = 0.5;
 if (truths.z) newNormal.z = 0.5;}

 //newNormal = p3d_NormalMatrix * newNormal;

 normal = normal * newNormal;
 //normal = newNormal;

 for (int i = 0; i < p3d_LightSource.length(); ++i) {

  if (p3d_LightSource[i].color.rgb.length() == 0){ continue; }

  vec3 lightDir = normalize(p3d_LightSource[i].position.xyz - (vertexPos.xyz * p3d_LightSource[i].position.w));
  float diffuseIntensity = dot(normal, lightDir);

  //if (abs(diffuseIntensity) > 0.99) {newColor = vec4(0.95, 0.9, 1.0, 1.0); break;}

  vec4 diffuseTemp = vec4( clamp( vec3(0.7, 0.7, 0.97) * p3d_LightSource[i].color.rgb * diffuseIntensity, 0,1), 0.0);
  newColor = clamp(newColor + diffuseTemp, vec4(0), vec4(1));

  float shadow = textureProj
   ( p3d_LightSource[i].shadowMap,
     shadowViewCoord[i]);
  newColor.rgb *= shadow;
  
  }
  newColor.w = clamp((newColor.x + newColor.y + newColor.z) /3, 0.4, 1);
  //newColor.w = 0.3;

p3d_fragColor = newColor;
}